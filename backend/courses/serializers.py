from urllib.parse import urlparse

from rest_framework import serializers

from .models import Course, Lesson, LessonProgress, ProjectSubmission


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "sequence_number"]


class CourseListSerializer(serializers.ModelSerializer):
    lessons = serializers.IntegerField(source="lessons.count", read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "description", "level", "weeks", "lessons"]


class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = serializers.IntegerField(source="lessons.count", read_only=True)
    lesson_list = LessonSerializer(source="lessons", many=True, read_only=True)
    is_enrolled = serializers.SerializerMethodField()

    def get_is_enrolled(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return obj.enrollments.filter(user=request.user).exists()

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "level", "weeks",
            "project", "outcomes", "lessons", "lesson_list", "is_enrolled",
        ]


class MyCourseSerializer(CourseListSerializer):
    """Course card + the logged-in student's progress."""
    completed_lessons = serializers.SerializerMethodField()

    class Meta(CourseListSerializer.Meta):
        fields = CourseListSerializer.Meta.fields + ["completed_lessons"]

    def get_completed_lessons(self, obj):
        user = self.context["request"].user
        return LessonProgress.objects.filter(user=user, lesson__course=obj).count()


class ProjectSubmissionSerializer(serializers.ModelSerializer):
    repo_url = serializers.URLField(max_length=300)
    notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    class Meta:
        model = ProjectSubmission
        fields = ["repo_url", "notes", "status", "feedback", "submitted_at"]
        read_only_fields = ["status", "feedback", "submitted_at"]

    def validate_repo_url(self, value):
        # Only web links. Blocks javascript:, ftp: and similar.
        if urlparse(value).scheme not in ("http", "https"):
            raise serializers.ValidationError("Enter a link that starts with http:// or https://")
        return value
