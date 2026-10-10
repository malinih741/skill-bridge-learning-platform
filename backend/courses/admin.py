from django.contrib import admin
from django.utils import timezone

from .models import (
    Certificate,
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    ProjectSubmission,
    Question,
    Quiz,
    QuizAttempt,
)
from .services import issue_certificate_if_eligible


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "weeks", "published")
    list_filter = ("level", "published")
    search_fields = ("title",)
    inlines = [LessonInline]


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "pass_mark")
    inlines = [QuestionInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "status", "enrolled_at")
    list_filter = ("status",)


admin.site.register(LessonProgress)


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "quiz", "score", "passed", "attempted_at")


@admin.register(ProjectSubmission)
class ProjectSubmissionAdmin(admin.ModelAdmin):
    """Review student projects: open one, set status + feedback, save."""
    list_display = ("user", "course", "status", "submitted_at")
    list_filter = ("status", "course")
    fields = ("user", "course", "repo_url", "notes", "status", "feedback",
              "submitted_at", "reviewed_by", "reviewed_at")
    readonly_fields = ("user", "course", "repo_url", "notes", "submitted_at",
                       "reviewed_by", "reviewed_at")
    actions = ["approve_selected"]

    def has_add_permission(self, request):
        return False

    def save_model(self, request, obj, form, change):
        if change and "status" in form.changed_data and obj.status != ProjectSubmission.Status.SUBMITTED:
            obj.reviewed_by = request.user
            obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
        if obj.status == ProjectSubmission.Status.APPROVED:
            issue_certificate_if_eligible(obj.user, obj.course)

    @admin.action(description="Approve selected projects")
    def approve_selected(self, request, queryset):
        count = 0
        for submission in queryset:
            submission.status = ProjectSubmission.Status.APPROVED
            submission.reviewed_by = request.user
            submission.reviewed_at = timezone.now()
            submission.save()
            issue_certificate_if_eligible(submission.user, submission.course)
            count += 1
        self.message_user(request, f"Approved {count} project(s).")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Certificates are issued automatically. Tick 'revoked' to cancel one."""
    list_display = ("certificate_number", "recipient_name", "course", "issued_at", "revoked")
    list_filter = ("revoked", "course")
    search_fields = ("certificate_number", "recipient_name")
    readonly_fields = ("user", "course", "certificate_number", "recipient_name", "issued_at")

    def has_add_permission(self, request):
        return False
