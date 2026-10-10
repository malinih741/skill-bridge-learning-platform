from django.contrib import admin

from .models import Course, Lesson


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "level", "weeks", "published")
    list_filter = ("level", "published")
    search_fields = ("title",)
    inlines = [LessonInline]
