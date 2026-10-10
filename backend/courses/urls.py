from django.urls import path

from .views import (
    CompleteLessonView,
    CourseDetailView,
    CourseLessonsView,
    CourseListView,
    CourseProgressView,
    CourseQuizzesView,
    EnrollView,
    MyCertificatesView,
    MyCoursesView,
    SubmitProjectView,
    SubmitQuizView,
    VerifyCertificateView,
)

urlpatterns = [
    path("courses/", CourseListView.as_view(), name="course-list"),
    path("courses/<int:pk>/", CourseDetailView.as_view(), name="course-detail"),
    path("courses/<int:pk>/enroll/", EnrollView.as_view(), name="course-enroll"),
    path("courses/<int:pk>/lessons/", CourseLessonsView.as_view(), name="course-lessons"),
    path("courses/<int:pk>/quizzes/", CourseQuizzesView.as_view(), name="course-quizzes"),
    path("courses/<int:pk>/progress/", CourseProgressView.as_view(), name="course-progress"),
    path("courses/<int:pk>/project/", SubmitProjectView.as_view(), name="course-project"),
    path("lessons/<int:pk>/complete/", CompleteLessonView.as_view(), name="lesson-complete"),
    path("quizzes/<int:pk>/submit/", SubmitQuizView.as_view(), name="quiz-submit"),
    path("certificates/verify/<str:number>/", VerifyCertificateView.as_view(), name="certificate-verify"),
    path("my-certificates/", MyCertificatesView.as_view(), name="my-certificates"),
    path("my-courses/", MyCoursesView.as_view(), name="my-courses"),
]
