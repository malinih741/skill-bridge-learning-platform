# SkillBridge – Skill Development & Certification Platform

A full-stack learning platform. Students enrol in courses, complete lessons, pass quizzes, submit a final project, and earn a **certificate that anyone can verify online**.

Built as a portfolio project with **React** and **Django REST Framework**.

![Home page](docs/screenshots/home.png)

## Features

**For students**
- Browse a course catalogue with search and level filter
- Create an account, log in and log out
- Enrol in a course and follow its lessons with a progress bar
- Take multiple-choice quizzes and see which answers were wrong
- Submit a final project link and read the reviewer's feedback
- Receive a certificate automatically when every requirement is met
- Print the certificate or save it as a PDF

**For the public**
- Verify any certificate by its number, with no login. The page shows the holder's name, the course and the issue date, and nothing private.

**For admins (Django admin panel)**
- Add and edit courses, lessons, quizzes and questions
- Review submitted projects: approve, or request changes with feedback
- Revoke a certificate if needed

## How a certificate is earned

A certificate is issued automatically once **all three** are true:

1. Every lesson in the course is marked complete
2. Every quiz in the course is passed
3. The final project is approved by a reviewer

The rules live in one place (`backend/courses/services.py`) and are checked every time a lesson is completed, a quiz is passed, or a project is approved. Each student can hold only one certificate per course.

## Screenshots

| Courses | Learning page |
|---|---|
| ![Courses](docs/screenshots/courses.png) | ![Learning page](docs/screenshots/learn.png) |

| Quiz result | Certificate |
|---|---|
| ![Quiz](docs/screenshots/quiz.png) | ![Certificate](docs/screenshots/certificate.png) |

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, React Router |
| Backend | Django, Django REST Framework, token authentication |
| Database | SQLite (development) |
| Testing | Django test framework (API tests) |

## Project structure

```
skillbridge/
├── frontend/              React app
│   └── src/
│       ├── components/    Navbar, CourseCard, Quiz, CompletionPanel, ...
│       ├── pages/         Home, Courses, Learn, Dashboard, Verify, ...
│       ├── context/       AuthContext (login state)
│       ├── hooks/         useFetch
│       └── services/      api.js (all backend calls)
├── backend/               Django project
│   ├── config/            settings and URL routing
│   ├── accounts/          register, login, logout, current user
│   └── courses/           courses, lessons, quizzes, projects, certificates
└── docs/screenshots/      images used in this README
```

## Run it on your computer

You need **Node.js**, **Python 3.12 or newer** and **Git**.

### 1. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_courses
python manage.py createsuperuser
python manage.py runserver
```

The API runs at http://127.0.0.1:8000/api/ and the admin panel at http://127.0.0.1:8000/admin/.

`seed_courses` adds five sample courses with lessons and quizzes. It is safe to run more than once.

### 2. Frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### 3. Run the tests

```bash
cd backend
python manage.py test
```

### Optional settings

Copy `backend/.env.example` to `backend/.env` to change the secret key, debug mode or allowed origins. Without it, safe development defaults are used. Set a real `DJANGO_SECRET_KEY` and `DJANGO_DEBUG=False` before putting the site online.

## API overview

| Method | Endpoint | Who | Purpose |
|---|---|---|---|
| POST | `/api/auth/register/` | Anyone | Create an account |
| POST | `/api/auth/login/` | Anyone | Log in, returns a token |
| POST | `/api/auth/logout/` | Student | Delete the token |
| GET | `/api/auth/me/` | Student | Current user |
| GET | `/api/courses/` | Anyone | Published courses |
| GET | `/api/courses/<id>/` | Anyone | Course details |
| POST | `/api/courses/<id>/enroll/` | Student | Enrol |
| GET | `/api/my-courses/` | Student | My courses with progress |
| GET | `/api/courses/<id>/lessons/` | Enrolled | Lessons and progress |
| POST | `/api/lessons/<id>/complete/` | Enrolled | Mark a lesson complete |
| GET | `/api/courses/<id>/quizzes/` | Enrolled | Questions (no answers included) |
| POST | `/api/quizzes/<id>/submit/` | Enrolled | Submit answers, get score |
| GET | `/api/courses/<id>/progress/` | Enrolled | What is left for the certificate |
| POST | `/api/courses/<id>/project/` | Enrolled | Submit the final project |
| GET | `/api/my-certificates/` | Student | My certificates |
| GET | `/api/certificates/verify/<number>/` | Anyone | Verify a certificate |

## Security and design decisions

- **Passwords are hashed** by Django. They are never stored as plain text, and weak passwords are rejected.
- **Quiz scores are calculated on the server.** The browser sends only the chosen options. A score sent by the browser is ignored, and the correct answers are never sent to the browser.
- **Access is checked on the server.** Lessons, quizzes and projects return an error for students who have not enrolled.
- **Actions are safe to repeat.** Enrolling or completing a lesson twice never creates duplicate rows (database unique constraints back this up).
- **Certificate numbers are random** (for example `SB-K7P2M-9XQ4R`), so the next one cannot be guessed. The verify page shows no email address.
- **Project links** must start with `http://` or `https://`, which blocks `javascript:` links, and open with `rel="noopener noreferrer"`.
- **Login and verify endpoints are rate limited** to slow down guessing.
- **Unpublished courses** are hidden from the public API.

## Known limitations

- Runs locally only. It is not deployed yet.
- Uses SQLite. A move to MySQL is planned.
- The login token is kept in the browser's local storage. A production version should use secure, HTTP-only cookies.
- No email verification and no password reset yet.
- Lesson text is starter content. Replace it in the admin panel.
- The certificate is printed to PDF from the browser, not generated on the server.
- There are no automated frontend tests yet.

## Roadmap

- [x] Course catalogue, accounts, enrolment
- [x] Lessons, progress tracking, quizzes
- [x] Project review and certificates with public verification
- [ ] MySQL database
- [ ] Deployment
- [ ] Password reset and email verification
- [ ] Frontend tests

## Author

Built by ** Built by Hema Malini** as a portfolio project.
