# SkillBridge – Skill Development & Certification Platform

A full-stack learning platform. Students enrol in courses, complete lessons, pass quizzes, submit a final project, and earn a **certificate that anyone can verify online**.

Built as a portfolio project with **React** and **Django REST Framework**.

![Home page](docs/screenshots/home.png)

## Live demo

- **Website:** https://tangerine-starship-6fa4ba.netlify.app
- **API:** https://hema1418.pythonanywhere.com/api/courses/

Create your own student account to try it. The demo runs on free hosting, so it can be slow on the first visit, and it may be offline for a short while if the free plan is not renewed.

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
| Database | MySQL 8.4 (SQLite is used automatically if no database is configured) |
| Testing | Django test framework (API tests) |
| Hosting | Netlify (frontend), PythonAnywhere free plan (backend) |

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

You need **Node.js**, **Python 3.12 or newer**, **MySQL 8.4 or newer** and **Git**.

### 1. Create the MySQL database

In a MySQL prompt (`mysql -u root -p`), run these. Choose your own password:

```sql
CREATE DATABASE skillbridge CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'skillbridge_user'@'localhost' IDENTIFIED BY 'choose-a-strong-password';
GRANT ALL PRIVILEGES ON skillbridge.* TO 'skillbridge_user'@'localhost';
GRANT ALL PRIVILEGES ON test_skillbridge.* TO 'skillbridge_user'@'localhost';
FLUSH PRIVILEGES;
```

The last `GRANT` lets the test command create its own temporary test database.

### 2. Backend

```bash
cd backend
copy .env.example .env         # Windows   (macOS / Linux: cp .env.example .env)
```

Open `backend/.env` and set `DB_PASSWORD` to the password you chose. This file is ignored by Git, so your password stays on your computer.

```bash
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

### 3. Frontend (in a second terminal)

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173.

### 4. Run the tests

```bash
cd backend
python manage.py test
```

### Settings (`backend/.env`)

| Setting | Purpose |
|---|---|
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | MySQL connection. Remove `DB_NAME` to use a local SQLite file instead. |
| `DJANGO_SECRET_KEY` | Set a long random value before putting the site online. |
| `DJANGO_DEBUG` | Set to `False` when the site is online. |
| `CORS_ALLOWED_ORIGINS` | Addresses the React app runs on. |

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

## Deployment

| Part | Where | Notes |
|---|---|---|
| React app | Netlify | Built with `VITE_API_URL` pointing at the API, then uploaded. `public/_redirects` makes page refreshes work. |
| Django API | PythonAnywhere (free plan) | Settings come from a server-side `.env` file with `DJANGO_DEBUG=False` and a generated secret key. |
| Database | SQLite on the live site, MySQL on my computer | The same settings file picks the database from `.env`. |

Live-site settings that matter (kept in `backend/.env` on the server, never in Git):

- `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`
- `CORS_ALLOWED_ORIGINS`: the address of the React site
- `CSRF_TRUSTED_ORIGINS`: the https address of the API, needed for the admin login

Build the frontend for the live API:

```bash
cd frontend
set VITE_API_URL=https://hema1418.pythonanywhere.com/api&& npm run build    # Windows
# VITE_API_URL=https://hema1418.pythonanywhere.com/api npm run build        # macOS / Linux
```

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

- The live site uses free hosting. It needs a monthly renewal click on PythonAnywhere and uses SQLite there, not MySQL.
- The login token is kept in the browser's local storage. A production version should use secure, HTTP-only cookies.
- No email verification and no password reset yet.
- Lesson text is starter content. Replace it in the admin panel.
- The certificate is printed to PDF from the browser, not generated on the server.
- There are no automated frontend tests yet.

## Roadmap

- [x] Course catalogue, accounts, enrolment
- [x] Lessons, progress tracking, quizzes
- [x] Project review and certificates with public verification
- [x] MySQL database
- [x] Deployment
- [ ] Password reset and email verification
- [ ] Frontend tests

## Author

Built by **Hema Malini Saravanan** as a portfolio project.
