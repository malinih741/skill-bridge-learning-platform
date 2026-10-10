from rest_framework import serializers

from .models import Course, Lesson


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

    class Meta:
        model = Course
        fields = [
            "id", "title", "description", "level", "weeks",
            "project", "outcomes", "lessons", "lesson_list",
        ]
