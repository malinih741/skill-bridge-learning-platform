from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Course, Enrollment

User = get_user_model()


class CourseApiTests(APITestCase):
    def setUp(self):
        self.published = Course.objects.create(
            title="Python Basics", description="Intro", published=True
        )
        self.hidden = Course.objects.create(
            title="Secret Draft", description="Not ready", published=False
        )

    def test_list_shows_only_published_courses(self):
        response = self.client.get(reverse("course-list"))
        self.assertEqual(response.status_code, 200)
        titles = [c["title"] for c in response.json()]
        self.assertIn("Python Basics", titles)
        self.assertNotIn("Secret Draft", titles)

    def test_detail_of_published_course(self):
        response = self.client.get(reverse("course-detail", args=[self.published.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Python Basics")
        self.assertFalse(response.json()["is_enrolled"])

    def test_detail_of_unpublished_course_is_404(self):
        response = self.client.get(reverse("course-detail", args=[self.hidden.id]))
        self.assertEqual(response.status_code, 404)


class EnrollmentTests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="SQL", description="d", published=True)
        self.draft = Course.objects.create(title="Draft", description="d", published=False)
        self.asha = User.objects.create_user("asha@example.com", "asha@example.com", "Str0ng-Pass-2026")
        self.ravi = User.objects.create_user("ravi@example.com", "ravi@example.com", "Str0ng-Pass-2026")

    def login_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_enrol_requires_login(self):
        response = self.client.post(reverse("course-enroll", args=[self.course.id]))
        self.assertEqual(response.status_code, 401)

    def test_enrol_twice_creates_one_row(self):
        self.login_as(self.asha)
        url = reverse("course-enroll", args=[self.course.id])
        self.assertEqual(self.client.post(url).status_code, 201)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(Enrollment.objects.filter(user=self.asha).count(), 1)

    def test_cannot_enrol_in_unpublished_course(self):
        self.login_as(self.asha)
        response = self.client.post(reverse("course-enroll", args=[self.draft.id]))
        self.assertEqual(response.status_code, 404)

    def test_my_courses_shows_only_own_enrolments(self):
        Enrollment.objects.create(user=self.asha, course=self.course)
        self.login_as(self.ravi)
        self.assertEqual(self.client.get(reverse("my-courses")).json(), [])
        self.login_as(self.asha)
        titles = [c["title"] for c in self.client.get(reverse("my-courses")).json()]
        self.assertEqual(titles, ["SQL"])

    def test_detail_reports_is_enrolled(self):
        Enrollment.objects.create(user=self.asha, course=self.course)
        self.login_as(self.asha)
        response = self.client.get(reverse("course-detail", args=[self.course.id]))
        self.assertTrue(response.json()["is_enrolled"])


from .models import Lesson, LessonProgress, Question, Quiz, QuizAttempt  # noqa: E402


class LearningTests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="Python", description="d", published=True)
        self.l1 = Lesson.objects.create(course=self.course, title="One", content="Hello", sequence_number=1)
        self.l2 = Lesson.objects.create(course=self.course, title="Two", content="World", sequence_number=2)
        self.quiz = Quiz.objects.create(course=self.course, title="Quiz", pass_mark=60)
        self.q1 = Question.objects.create(quiz=self.quiz, question_text="Q1", options=["a", "b", "c"], correct_answer=1, order=1)
        self.q2 = Question.objects.create(quiz=self.quiz, question_text="Q2", options=["a", "b"], correct_answer=0, order=2)
        self.asha = User.objects.create_user("asha@example.com", "asha@example.com", "Str0ng-Pass-2026")
        self.outsider = User.objects.create_user("lee@example.com", "lee@example.com", "Str0ng-Pass-2026")
        Enrollment.objects.create(user=self.asha, course=self.course)

    def login_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    # --- lessons ---
    def test_lessons_need_enrolment(self):
        self.login_as(self.outsider)
        self.assertEqual(self.client.get(reverse("course-lessons", args=[self.course.id])).status_code, 403)
        self.assertEqual(self.client.post(reverse("lesson-complete", args=[self.l1.id])).status_code, 403)

    def test_lessons_need_login(self):
        self.assertEqual(self.client.get(reverse("course-lessons", args=[self.course.id])).status_code, 401)

    def test_complete_lesson_twice_creates_one_record(self):
        self.login_as(self.asha)
        url = reverse("lesson-complete", args=[self.l1.id])
        self.assertEqual(self.client.post(url).status_code, 201)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(LessonProgress.objects.filter(user=self.asha).count(), 1)

    def test_progress_is_reported(self):
        self.login_as(self.asha)
        self.client.post(reverse("lesson-complete", args=[self.l1.id]))
        data = self.client.get(reverse("course-lessons", args=[self.course.id])).json()
        self.assertEqual((data["completed"], data["total"]), (1, 2))
        mine = self.client.get(reverse("my-courses")).json()
        self.assertEqual(mine[0]["completed_lessons"], 1)

    # --- quizzes ---
    def test_quiz_questions_do_not_leak_correct_answers(self):
        self.login_as(self.asha)
        response = self.client.get(reverse("course-quizzes", args=[self.course.id]))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("correct_answer", response.content.decode())

    def test_score_is_calculated_on_the_server(self):
        self.login_as(self.asha)
        url = reverse("quiz-submit", args=[self.quiz.id])
        perfect = self.client.post(url, {"answers": {str(self.q1.id): 1, str(self.q2.id): 0}}, format="json")
        self.assertEqual(perfect.json()["score"], 100)
        self.assertTrue(perfect.json()["passed"])
        wrong = self.client.post(url, {"answers": {str(self.q1.id): 0, str(self.q2.id): 1}}, format="json")
        self.assertEqual(wrong.json()["score"], 0)
        self.assertFalse(wrong.json()["passed"])
        self.assertEqual(QuizAttempt.objects.filter(user=self.asha).count(), 2)

    def test_client_cannot_send_its_own_score(self):
        self.login_as(self.asha)
        url = reverse("quiz-submit", args=[self.quiz.id])
        response = self.client.post(
            url, {"score": 100, "answers": {str(self.q1.id): 0, str(self.q2.id): 1}}, format="json"
        )
        self.assertEqual(response.json()["score"], 0)

    def test_invalid_answers_are_rejected(self):
        self.login_as(self.asha)
        url = reverse("quiz-submit", args=[self.quiz.id])
        self.assertEqual(self.client.post(url, {"answers": {str(self.q1.id): 1}}, format="json").status_code, 400)
        self.assertEqual(
            self.client.post(url, {"answers": {str(self.q1.id): 99, str(self.q2.id): 0}}, format="json").status_code, 400
        )
        self.assertEqual(self.client.post(url, {"answers": "nope"}, format="json").status_code, 400)

    def test_quiz_needs_enrolment(self):
        self.login_as(self.outsider)
        url = reverse("quiz-submit", args=[self.quiz.id])
        self.assertEqual(self.client.post(url, {"answers": {}}, format="json").status_code, 403)


from .models import Certificate, ProjectSubmission  # noqa: E402
from .services import issue_certificate_if_eligible  # noqa: E402


class CertificateTests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="Python", description="d", published=True)
        self.lesson = Lesson.objects.create(course=self.course, title="One", content="x", sequence_number=1)
        self.quiz = Quiz.objects.create(course=self.course, title="Quiz", pass_mark=60)
        self.question = Question.objects.create(
            quiz=self.quiz, question_text="Q", options=["a", "b"], correct_answer=0, order=1
        )
        self.asha = User.objects.create_user(
            "asha@example.com", "asha@example.com", "Str0ng-Pass-2026", first_name="Asha Kumar"
        )
        self.outsider = User.objects.create_user("lee@example.com", "lee@example.com", "Str0ng-Pass-2026")
        Enrollment.objects.create(user=self.asha, course=self.course)

    def login_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def finish_lesson(self):
        return self.client.post(reverse("lesson-complete", args=[self.lesson.id]))

    def take_quiz(self, answer):
        return self.client.post(
            reverse("quiz-submit", args=[self.quiz.id]),
            {"answers": {str(self.question.id): answer}},
            format="json",
        )

    def submit_project(self, url="https://github.com/asha/project"):
        return self.client.post(
            reverse("course-project", args=[self.course.id]),
            {"repo_url": url, "notes": "done"},
            format="json",
        )

    def approve_project(self):
        ProjectSubmission.objects.filter(user=self.asha, course=self.course).update(
            status=ProjectSubmission.Status.APPROVED
        )
        return issue_certificate_if_eligible(self.asha, self.course)

    # --- project submission ---
    def test_project_needs_enrolment(self):
        self.login_as(self.outsider)
        self.assertEqual(self.submit_project().status_code, 403)

    def test_project_link_must_be_http_or_https(self):
        self.login_as(self.asha)
        self.assertEqual(self.submit_project("javascript:alert(1)").status_code, 400)
        self.assertEqual(self.submit_project("not a url").status_code, 400)

    def test_resubmit_after_changes_requested_then_locked_when_approved(self):
        self.login_as(self.asha)
        self.assertEqual(self.submit_project().status_code, 201)
        ProjectSubmission.objects.update(status="changes_requested", feedback="Add a README")
        again = self.submit_project("https://github.com/asha/project-v2")
        self.assertEqual(again.status_code, 200)
        self.assertEqual(again.json()["status"], "submitted")
        self.assertEqual(again.json()["feedback"], "")
        self.assertEqual(ProjectSubmission.objects.count(), 1)
        ProjectSubmission.objects.update(status="approved")
        self.assertEqual(self.submit_project().status_code, 400)

    def test_student_cannot_approve_own_project(self):
        self.login_as(self.asha)
        response = self.client.post(
            reverse("course-project", args=[self.course.id]),
            {"repo_url": "https://github.com/a/b", "status": "approved"},
            format="json",
        )
        self.assertEqual(response.json()["status"], "submitted")

    # --- certificate rules ---
    def test_no_certificate_until_everything_is_done(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(0)
        self.assertIsNone(self.approve_project())  # no project submitted yet
        self.assertEqual(Certificate.objects.count(), 0)

    def test_failed_quiz_blocks_certificate(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(1)  # wrong
        self.submit_project()
        self.assertIsNone(self.approve_project())

    def test_unapproved_project_blocks_certificate(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(0)
        self.submit_project()
        self.assertEqual(Certificate.objects.count(), 0)

    def test_full_flow_issues_one_certificate(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(0)
        self.submit_project()
        certificate = self.approve_project()
        self.assertIsNotNone(certificate)
        self.assertTrue(certificate.certificate_number.startswith("SB-"))
        self.assertEqual(certificate.recipient_name, "Asha Kumar")
        # asking again must not create a second one
        issue_certificate_if_eligible(self.asha, self.course)
        self.assertEqual(Certificate.objects.count(), 1)
        self.assertEqual(Enrollment.objects.get(user=self.asha).status, "completed")

    def test_certificate_issued_when_last_step_is_the_lesson(self):
        self.login_as(self.asha)
        self.take_quiz(0)
        self.submit_project()
        ProjectSubmission.objects.update(status="approved")
        response = self.finish_lesson()
        self.assertIsNotNone(response.json()["certificate"])
        self.assertEqual(Certificate.objects.count(), 1)

    def test_progress_endpoint(self):
        self.login_as(self.asha)
        self.finish_lesson()
        data = self.client.get(reverse("course-progress", args=[self.course.id])).json()
        self.assertEqual(data["lessons"], {"done": 1, "total": 1})
        self.assertEqual(data["quizzes"], {"passed": 0, "total": 1})
        self.assertFalse(data["eligible"])
        self.assertIsNone(data["certificate"])

    def test_my_certificates_lists_only_own(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(0)
        self.submit_project()
        self.approve_project()
        self.assertEqual(len(self.client.get(reverse("my-certificates")).json()), 1)
        self.login_as(self.outsider)
        self.assertEqual(self.client.get(reverse("my-certificates")).json(), [])

    # --- public verification ---
    def test_public_verification_valid_invalid_and_revoked(self):
        self.login_as(self.asha)
        self.finish_lesson()
        self.take_quiz(0)
        self.submit_project()
        certificate = self.approve_project()
        self.client.credentials()  # logged out: anyone can verify

        url = reverse("certificate-verify", args=[certificate.certificate_number.lower()])
        ok = self.client.get(url)
        self.assertEqual(ok.status_code, 200)
        body = ok.json()
        self.assertTrue(body["valid"])
        self.assertEqual(body["recipient_name"], "Asha Kumar")
        self.assertEqual(body["course_title"], "Python")
        self.assertNotIn("asha@example.com", ok.content.decode())

        missing = self.client.get(reverse("certificate-verify", args=["SB-AAAAA-BBBBB"]))
        self.assertEqual(missing.status_code, 404)
        self.assertFalse(missing.json()["valid"])

        certificate.revoked = True
        certificate.save()
        revoked = self.client.get(url)
        self.assertFalse(revoked.json()["valid"])
