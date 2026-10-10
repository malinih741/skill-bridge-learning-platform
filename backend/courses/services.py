import secrets

from .models import (
    Certificate,
    Enrollment,
    LessonProgress,
    ProjectSubmission,
    QuizAttempt,
)

# No 0/O/1/I so numbers are easy to read out and type.
ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def generate_certificate_number():
    """Random and unpredictable, e.g. SB-K7P2M-9XQ4R. Nobody can guess the next one."""
    while True:
        raw = "".join(secrets.choice(ALPHABET) for _ in range(10))
        number = f"SB-{raw[:5]}-{raw[5:]}"
        if not Certificate.objects.filter(certificate_number=number).exists():
            return number


def completion_status(user, course):
    """The rules for a certificate: every lesson done, every quiz passed, project approved."""
    total_lessons = course.lessons.count()
    done_lessons = LessonProgress.objects.filter(user=user, lesson__course=course).count()

    quizzes = course.quizzes.filter(questions__isnull=False).distinct()
    total_quizzes = quizzes.count()
    passed_quizzes = (
        QuizAttempt.objects.filter(user=user, quiz__in=quizzes, passed=True)
        .values("quiz")
        .distinct()
        .count()
    )

    submission = ProjectSubmission.objects.filter(user=user, course=course).first()
    project_approved = bool(submission and submission.status == ProjectSubmission.Status.APPROVED)

    eligible = (
        total_lessons > 0
        and done_lessons >= total_lessons
        and passed_quizzes >= total_quizzes
        and project_approved
    )
    return {
        "lessons": {"done": done_lessons, "total": total_lessons},
        "quizzes": {"passed": passed_quizzes, "total": total_quizzes},
        "submission": submission,
        "eligible": eligible,
    }


def issue_certificate_if_eligible(user, course):
    """Safe to call any time and any number of times: at most one certificate per student+course."""
    if not Enrollment.objects.filter(user=user, course=course).exists():
        return None
    if not completion_status(user, course)["eligible"]:
        return None
    certificate, created = Certificate.objects.get_or_create(
        user=user,
        course=course,
        defaults={
            "recipient_name": user.first_name or user.email,
            "certificate_number": generate_certificate_number(),
        },
    )
    if created:
        Enrollment.objects.filter(user=user, course=course).update(status=Enrollment.Status.COMPLETED)
    return certificate
