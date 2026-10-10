from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import (
    Certificate,
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    ProjectSubmission,
    Quiz,
    QuizAttempt,
)
from .serializers import (
    CourseDetailSerializer,
    CourseListSerializer,
    MyCourseSerializer,
    ProjectSubmissionSerializer,
)
from .services import completion_status, issue_certificate_if_eligible


def require_enrolment(user, course):
    """Lessons and quizzes are only for students enrolled in the course."""
    if not Enrollment.objects.filter(user=user, course=course).exists():
        raise PermissionDenied("Enrol in this course to access it.")


class CourseListView(generics.ListAPIView):
    """GET /api/courses/ - only published courses."""
    serializer_class = CourseListSerializer

    def get_queryset(self):
        return Course.objects.filter(published=True)


class CourseDetailView(generics.RetrieveAPIView):
    """GET /api/courses/<id>/ - unpublished courses return 404."""
    serializer_class = CourseDetailSerializer

    def get_queryset(self):
        return Course.objects.filter(published=True)


class EnrollView(APIView):
    """POST /api/courses/<id>/enroll/ - safe to call twice (no duplicate rows)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        _, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({"enrolled": True, "course": course.id}, status=201 if created else 200)


class MyCoursesView(generics.ListAPIView):
    """GET /api/my-courses/ - only the logged-in student's courses, with progress."""
    serializer_class = MyCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(published=True, enrollments__user=self.request.user)


class CourseLessonsView(APIView):
    """GET /api/courses/<id>/lessons/ - lesson content + this student's progress."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        require_enrolment(request.user, course)
        done = set(
            LessonProgress.objects.filter(user=request.user, lesson__course=course)
            .values_list("lesson_id", flat=True)
        )
        lessons = [
            {
                "id": lesson.id,
                "title": lesson.title,
                "content": lesson.content,
                "sequence_number": lesson.sequence_number,
                "completed": lesson.id in done,
            }
            for lesson in course.lessons.all()
        ]
        return Response(
            {
                "course": {"id": course.id, "title": course.title},
                "lessons": lessons,
                "completed": len(done),
                "total": len(lessons),
            }
        )


class CompleteLessonView(APIView):
    """POST /api/lessons/<id>/complete/ - repeating it never creates duplicates."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk, course__published=True)
        require_enrolment(request.user, lesson.course)
        _, created = LessonProgress.objects.get_or_create(user=request.user, lesson=lesson)
        certificate = issue_certificate_if_eligible(request.user, lesson.course)
        return Response(
            {
                "completed": True,
                "lesson": lesson.id,
                "certificate": certificate.certificate_number if certificate else None,
            },
            status=201 if created else 200,
        )


class CourseQuizzesView(APIView):
    """GET /api/courses/<id>/quizzes/ - questions WITHOUT the correct answers."""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        require_enrolment(request.user, course)
        data = []
        for quiz in course.quizzes.prefetch_related("questions"):
            best = QuizAttempt.objects.filter(user=request.user, quiz=quiz).order_by("-score").first()
            data.append(
                {
                    "id": quiz.id,
                    "title": quiz.title,
                    "pass_mark": quiz.pass_mark,
                    "best_score": best.score if best else None,
                    "passed": QuizAttempt.objects.filter(
                        user=request.user, quiz=quiz, passed=True
                    ).exists(),
                    "questions": [
                        {"id": q.id, "text": q.question_text, "options": q.options}
                        for q in quiz.questions.all()
                    ],
                }
            )
        return Response(data)


class SubmitQuizView(APIView):
    """POST /api/quizzes/<id>/submit/  body: {"answers": {"<question_id>": <option_index>}}

    The score is calculated here on the server. A score sent by the browser is never trusted.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk, course__published=True)
        require_enrolment(request.user, quiz.course)

        questions = list(quiz.questions.all())
        if not questions:
            raise ValidationError({"detail": "This quiz has no questions yet."})

        answers = request.data.get("answers")
        if not isinstance(answers, dict):
            raise ValidationError({"detail": "Send your answers as an object."})

        results = {}
        correct = 0
        for question in questions:
            choice = answers.get(str(question.id))
            valid = (
                isinstance(choice, int)
                and not isinstance(choice, bool)
                and 0 <= choice < len(question.options)
            )
            if not valid:
                raise ValidationError({"detail": "Answer every question with one of the listed options."})
            is_right = choice == question.correct_answer
            results[str(question.id)] = is_right
            correct += is_right

        score = round(100 * correct / len(questions))
        passed = score >= quiz.pass_mark
        QuizAttempt.objects.create(user=request.user, quiz=quiz, score=score, passed=passed)
        certificate = issue_certificate_if_eligible(request.user, quiz.course) if passed else None

        return Response(
            {
                "certificate": certificate.certificate_number if certificate else None,
                "score": score,
                "passed": passed,
                "pass_mark": quiz.pass_mark,
                "correct": correct,
                "total": len(questions),
                "results": results,
            }
        )


# ---------------------------------------------------------------- projects & certificates


class CourseProgressView(APIView):
    """GET /api/courses/<id>/progress/ - what is left before the certificate?"""
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        require_enrolment(request.user, course)
        status = completion_status(request.user, course)
        certificate = Certificate.objects.filter(
            user=request.user, course=course, revoked=False
        ).first()
        submission = status["submission"]
        return Response(
            {
                "lessons": status["lessons"],
                "quizzes": status["quizzes"],
                "project": ProjectSubmissionSerializer(submission).data if submission else None,
                "eligible": status["eligible"],
                "certificate": (
                    {
                        "number": certificate.certificate_number,
                        "issued_at": certificate.issued_at,
                    }
                    if certificate
                    else None
                ),
            }
        )


class SubmitProjectView(APIView):
    """POST /api/courses/<id>/project/ - submit (or re-submit after changes were requested)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        require_enrolment(request.user, course)
        existing = ProjectSubmission.objects.filter(user=request.user, course=course).first()
        if existing and existing.status == ProjectSubmission.Status.APPROVED:
            raise ValidationError({"detail": "Your project is already approved."})

        serializer = ProjectSubmissionSerializer(existing, data=request.data)
        serializer.is_valid(raise_exception=True)
        submission = serializer.save(
            user=request.user,
            course=course,
            status=ProjectSubmission.Status.SUBMITTED,
            feedback="",
            reviewed_at=None,
            reviewed_by=None,
        )
        return Response(
            ProjectSubmissionSerializer(submission).data, status=201 if existing is None else 200
        )


class MyCertificatesView(APIView):
    """GET /api/my-certificates/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        certificates = Certificate.objects.filter(user=request.user, revoked=False).select_related("course")
        return Response(
            [
                {
                    "number": c.certificate_number,
                    "course_title": c.course.title,
                    "issued_at": c.issued_at,
                }
                for c in certificates
            ]
        )


class VerifyCertificateView(APIView):
    """GET /api/certificates/verify/<number>/ - public, no login. Shows no email or other private data."""
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "verify"

    def get(self, request, number):
        certificate = (
            Certificate.objects.select_related("course")
            .filter(certificate_number=number.strip().upper())
            .first()
        )
        if certificate is None:
            return Response(
                {"valid": False, "detail": "No certificate was found with this number."}, status=404
            )
        if certificate.revoked:
            return Response({"valid": False, "detail": "This certificate has been revoked."})
        return Response(
            {
                "valid": True,
                "certificate_number": certificate.certificate_number,
                "recipient_name": certificate.recipient_name,
                "course_title": certificate.course.title,
                "level": certificate.course.level,
                "issued_at": certificate.issued_at,
            }
        )
