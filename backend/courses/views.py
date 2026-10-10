from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Enrollment
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


class EnrollView(APIView):
    """POST /api/courses/<id>/enroll/ - safe to call twice (no duplicate rows)."""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        course = get_object_or_404(Course, pk=pk, published=True)
        _, created = Enrollment.objects.get_or_create(user=request.user, course=course)
        return Response({"enrolled": True, "course": course.id}, status=201 if created else 200)


class MyCoursesView(generics.ListAPIView):
    """GET /api/my-courses/ - only the logged-in student's courses."""
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Course.objects.filter(published=True, enrollments__user=self.request.user)
