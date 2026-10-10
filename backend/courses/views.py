from rest_framework import generics

from .models import Course
from .serializers import CourseDetailSerializer, CourseListSerializer


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
