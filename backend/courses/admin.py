from django.contrib import admin

from .models import Course, Enrollment, Lesson, LessonProgress, Question, Quiz, QuizAttempt


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
