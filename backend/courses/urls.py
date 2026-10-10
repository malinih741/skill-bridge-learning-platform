from django.urls import path

from .views import CourseDetailView, CourseListView, EnrollView, MyCoursesView

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:pk>/enroll/", EnrollView.as_view(), name="course-enroll"),
    path("my-courses/", MyCoursesView.as_view(), name="my-courses"),
]
