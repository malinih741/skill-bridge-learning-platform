from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Enrollment, Lesson, LessonProgress, Quiz, QuizAttempt
from .serializers import CourseDetailSerializer, CourseListSerializer, MyCourseSerializer


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
        return Response({"completed": True, "lesson": lesson.id}, status=201 if created else 200)


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

        return Response(
            {
                "score": score,
                "passed": passed,
                "pass_mark": quiz.pass_mark,
                "correct": correct,
                "total": len(questions),
                "results": results,
            }
        )
