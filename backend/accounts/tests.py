from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

User = get_user_model()
GOOD_PASSWORD = "Str0ng-Pass-2026"


class AuthApiTests(APITestCase):
    def register(self, email="asha@example.com", password=GOOD_PASSWORD):
        return self.client.post(
            reverse("auth-register"),
            {"name": "Asha", "email": email, "password": password},
            format="json",
        )

    def test_register_creates_user_with_hashed_password(self):
        response = self.register()
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.json())
        user = User.objects.get(email="asha@example.com")
        self.assertNotEqual(user.password, GOOD_PASSWORD)
        self.assertTrue(user.check_password(GOOD_PASSWORD))

    def test_register_duplicate_email_rejected_case_insensitive(self):
        self.register()
        response = self.register(email="ASHA@example.com")
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", response.json())

    def test_register_weak_password_rejected(self):
        response = self.register(password="12345678")
        self.assertEqual(response.status_code, 400)
        self.assertIn("password", response.json())

    def test_login_success_and_failure(self):
        self.register()
        ok = self.client.post(
            reverse("auth-login"),
            {"email": "asha@example.com", "password": GOOD_PASSWORD},
            format="json",
        )
        self.assertEqual(ok.status_code, 200)
        self.assertIn("token", ok.json())
        bad = self.client.post(
            reverse("auth-login"),
            {"email": "asha@example.com", "password": "wrong-password"},
            format="json",
        )
        self.assertEqual(bad.status_code, 400)

    def test_me_requires_login(self):
        self.assertEqual(self.client.get(reverse("auth-me")).status_code, 401)

    def test_me_and_logout_with_token(self):
        token = self.register().json()["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        me = self.client.get(reverse("auth-me"))
        self.assertEqual(me.status_code, 200)
        self.assertEqual(me.json()["email"], "asha@example.com")
        self.assertEqual(me.json()["role"], "student")
        self.assertEqual(self.client.post(reverse("auth-logout")).status_code, 204)
        self.assertFalse(Token.objects.filter(key=token).exists())
