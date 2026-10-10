from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from .models import Course, Enrollment

User = get_user_model()


class CourseApiTests(APITestCase):
    def setUp(self):
        self.published = Course.objects.create(
            title="Python Basics", description="Intro", published=True
        )
        self.hidden = Course.objects.create(
            title="Secret Draft", description="Not ready", published=False
        )

    def test_list_shows_only_published_courses(self):
        response = self.client.get(reverse("course-list"))
        self.assertEqual(response.status_code, 200)
        titles = [c["title"] for c in response.json()]
        self.assertIn("Python Basics", titles)
        self.assertNotIn("Secret Draft", titles)

    def test_detail_of_published_course(self):
        response = self.client.get(reverse("course-detail", args=[self.published.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "Python Basics")
        self.assertFalse(response.json()["is_enrolled"])

    def test_detail_of_unpublished_course_is_404(self):
        response = self.client.get(reverse("course-detail", args=[self.hidden.id]))
        self.assertEqual(response.status_code, 404)


class EnrollmentTests(APITestCase):
    def setUp(self):
        self.course = Course.objects.create(title="SQL", description="d", published=True)
        self.draft = Course.objects.create(title="Draft", description="d", published=False)
        self.asha = User.objects.create_user("asha@example.com", "asha@example.com", "Str0ng-Pass-2026")
        self.ravi = User.objects.create_user("ravi@example.com", "ravi@example.com", "Str0ng-Pass-2026")

    def login_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_enrol_requires_login(self):
        response = self.client.post(reverse("course-enroll", args=[self.course.id]))
        self.assertEqual(response.status_code, 401)

    def test_enrol_twice_creates_one_row(self):
        self.login_as(self.asha)
        url = reverse("course-enroll", args=[self.course.id])
        self.assertEqual(self.client.post(url).status_code, 201)
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(Enrollment.objects.filter(user=self.asha).count(), 1)

    def test_cannot_enrol_in_unpublished_course(self):
        self.login_as(self.asha)
        response = self.client.post(reverse("course-enroll", args=[self.draft.id]))
        self.assertEqual(response.status_code, 404)

    def test_my_courses_shows_only_own_enrolments(self):
        Enrollment.objects.create(user=self.asha, course=self.course)
        self.login_as(self.ravi)
        self.assertEqual(self.client.get(reverse("my-courses")).json(), [])
        self.login_as(self.asha)
        titles = [c["title"] for c in self.client.get(reverse("my-courses")).json()]
        self.assertEqual(titles, ["SQL"])

    def test_detail_reports_is_enrolled(self):
        Enrollment.objects.create(user=self.asha, course=self.course)
        self.login_as(self.asha)
        response = self.client.get(reverse("course-detail", args=[self.course.id]))
        self.assertTrue(response.json()["is_enrolled"])
