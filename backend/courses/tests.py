from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Course


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

    def test_detail_of_unpublished_course_is_404(self):
        response = self.client.get(reverse("course-detail", args=[self.hidden.id]))
        self.assertEqual(response.status_code, 404)
