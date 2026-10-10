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
