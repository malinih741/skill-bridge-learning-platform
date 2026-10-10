from django.conf import settings
from django.db import models


class Course(models.Model):
    class Level(models.TextChoices):
        BEGINNER = "Beginner", "Beginner"
        INTERMEDIATE = "Intermediate", "Intermediate"
        ADVANCED = "Advanced", "Advanced"

    title = models.CharField(max_length=200)
    description = models.TextField()
    level = models.CharField(max_length=20, choices=Level.choices, default=Level.BEGINNER)
    weeks = models.PositiveIntegerField(default=1)
    project = models.CharField(max_length=200, blank=True)
    outcomes = models.JSONField(default=list, blank=True)
    published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return self.title


class Lesson(models.Model):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    content = models.TextField(blank=True)
    sequence_number = models.PositiveIntegerField()

    class Meta:
        ordering = ["sequence_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "sequence_number"], name="unique_lesson_order_per_course"
            )
        ]

    def __str__(self):
        return f"{self.course.title} - {self.sequence_number}. {self.title}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="enrollments", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["-enrolled_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="unique_enrollment_per_user_course")
        ]

    def __str__(self):
        return f"{self.user} -> {self.course}"


class LessonProgress(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="lesson_progress", on_delete=models.CASCADE
    )
    lesson = models.ForeignKey(Lesson, related_name="progress", on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "lesson"], name="unique_progress_per_user_lesson")
        ]

    def __str__(self):
        return f"{self.user} completed {self.lesson}"


class Quiz(models.Model):
    course = models.ForeignKey(Course, related_name="quizzes", on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    pass_mark = models.PositiveSmallIntegerField(default=60, help_text="Percentage needed to pass")

    class Meta:
        verbose_name_plural = "quizzes"

    def __str__(self):
        return f"{self.course.title}: {self.title}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question_text = models.CharField(max_length=300)
    options = models.JSONField(default=list, help_text='List of choices, e.g. ["a", "b", "c"]')
    correct_answer = models.PositiveSmallIntegerField(
        help_text="Position of the right option, starting at 0 (first option = 0)"
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def clean(self):
        from django.core.exceptions import ValidationError

        if not isinstance(self.options, list) or len(self.options) < 2:
            raise ValidationError("Provide at least two options as a list.")
        if self.correct_answer >= len(self.options):
            raise ValidationError("correct_answer must be the position (from 0) of the right option.")

    def __str__(self):
        return self.question_text


class QuizAttempt(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="quiz_attempts", on_delete=models.CASCADE
    )
    quiz = models.ForeignKey(Quiz, related_name="attempts", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(help_text="Percentage, calculated by the server")
    passed = models.BooleanField(default=False)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-attempted_at"]

    def __str__(self):
        return f"{self.user} - {self.quiz} - {self.score}%"


class ProjectSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted (waiting for review)"
        APPROVED = "approved", "Approved"
        CHANGES_REQUESTED = "changes_requested", "Changes requested"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="project_submissions", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="project_submissions", on_delete=models.CASCADE)
    repo_url = models.URLField(max_length=300)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        related_name="reviewed_projects", on_delete=models.SET_NULL,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="one_project_per_user_course")
        ]

    def __str__(self):
        return f"{self.user} - {self.course} ({self.status})"


class Certificate(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name="certificates", on_delete=models.CASCADE
    )
    course = models.ForeignKey(Course, related_name="certificates", on_delete=models.CASCADE)
    certificate_number = models.CharField(max_length=30, unique=True, editable=False)
    recipient_name = models.CharField(max_length=150, help_text="Name printed on the certificate")
    issued_at = models.DateTimeField(auto_now_add=True)
    revoked = models.BooleanField(default=False)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "course"], name="one_certificate_per_user_course")
        ]

    def __str__(self):
        return f"{self.certificate_number} - {self.recipient_name}"
