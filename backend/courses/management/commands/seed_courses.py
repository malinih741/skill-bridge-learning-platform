from django.core.management.base import BaseCommand

from courses.models import Course, Lesson, Question, Quiz

# (title, level, weeks, project, description, outcomes, lesson titles, quiz questions)
# quiz question = (text, options, index of the correct option starting at 0)
COURSES = [
    ("HTML & CSS Foundations", "Beginner", 2, "Personal portfolio page",
     "Build and style responsive web pages from scratch using semantic HTML, Flexbox and Grid.",
     ["Structure pages with semantic HTML", "Style layouts with Flexbox and Grid", "Make pages mobile-friendly"],
     ["Intro to HTML", "Text, links and images", "Semantic layout", "CSS selectors", "Flexbox", "Grid", "Responsive design"],
     [("Which tag creates the largest heading?", ["<h1>", "<head>", "<header>", "<title>"], 0),
      ("Which CSS property changes text colour?", ["font-color", "color", "text-style", "foreground"], 1),
      ("Which CSS layout system works in rows AND columns at once?", ["Flexbox", "Float", "Grid", "Position"], 2)]),
    ("JavaScript Fundamentals", "Beginner", 3, "To-do list app",
     "Learn variables, functions, arrays, objects and the DOM by building small interactive tools.",
     ["Write and debug JavaScript", "Handle events and update the DOM", "Fetch data from an API"],
     ["Variables and types", "Functions", "Arrays and objects", "The DOM", "Events", "Fetch API"],
     [("Which keyword declares a variable that cannot be reassigned?", ["var", "let", "const", "static"], 2),
      ("What does typeof \"hello\" return?", ["string", "text", "char", "word"], 0),
      ("Which array method adds an item to the end?", ["push", "pop", "shift", "slice"], 0)]),
    ("Python Basics", "Beginner", 3, "Command-line expense tracker",
     "Start programming with Python: data types, control flow, functions and simple classes.",
     ["Write clear Python functions", "Work with lists and dictionaries", "Read and write files"],
     ["Hello Python", "Data types", "Control flow", "Functions", "Lists and dictionaries", "Files", "Classes"],
     [("Which keyword defines a function in Python?", ["func", "def", "function", "lambda"], 1),
      ("What does len([1, 2, 3]) return?", ["2", "3", "4", "Error"], 1),
      ("Which data type stores key-value pairs?", ["list", "tuple", "dict", "set"], 2)]),
    ("SQL Basics", "Intermediate", 2, "Library database",
     "Design tables and query data with SELECT, JOIN, GROUP BY and constraints.",
     ["Design relational tables", "Join and aggregate data", "Use keys and constraints"],
     ["Tables and keys", "SELECT", "Filtering", "JOIN", "GROUP BY"],
     [("Which clause filters rows?", ["WHERE", "ORDER BY", "GROUP BY", "LIMIT"], 0),
      ("Which JOIN returns only rows that match in both tables?", ["LEFT JOIN", "INNER JOIN", "FULL JOIN", "CROSS JOIN"], 1),
      ("Which constraint uniquely identifies each row?", ["FOREIGN KEY", "INDEX", "PRIMARY KEY", "CHECK"], 2)]),
    ("Beginner Web Projects", "Intermediate", 3, "Weather dashboard",
     "Combine HTML, CSS and JavaScript into complete projects you can publish on GitHub.",
     ["Plan a small project", "Use Git and GitHub", "Deploy a static site"],
     ["Plan the project", "Git and GitHub", "Build the UI", "Connect an API", "Deploy"],
     [("Which Git command records your staged changes?", ["git push", "git commit", "git clone", "git pull"], 1),
      ("Which file lists the files Git should ignore?", [".gitignore", "README.md", "package.json", "index.html"], 0),
      ("What does git push do?", ["Downloads changes", "Uploads your commits to GitHub", "Deletes a branch", "Creates a repository"], 1)]),
]


def lesson_text(title):
    return (
        f"{title}\n\n"
        f"In this lesson you will learn the key ideas behind \"{title.lower()}\" and try them yourself.\n\n"
        "Practice: write a small example, run it, then change one thing and see what happens.\n\n"
        "(Starter text. Replace it with your own lesson content in the admin panel.)"
    )


class Command(BaseCommand):
    help = "Load sample courses, lessons and quizzes (safe to run more than once)."

    def handle(self, *args, **options):
        for title, level, weeks, project, desc, outcomes, lessons, questions in COURSES:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults=dict(level=level, weeks=weeks, project=project,
                              description=desc, outcomes=outcomes, published=True),
            )
            self.stdout.write(f"{'Added' if created else 'Checked'}: {title}")

            for number, lesson_title in enumerate(lessons, start=1):
                lesson, _ = Lesson.objects.get_or_create(
                    course=course, sequence_number=number, defaults={"title": lesson_title}
                )
                if not lesson.content:
                    lesson.content = lesson_text(lesson.title)
                    lesson.save(update_fields=["content"])

            quiz, quiz_created = Quiz.objects.get_or_create(
                course=course, title=f"{title} quiz", defaults={"pass_mark": 60}
            )
            if quiz_created:
                for order, (text, options_, correct) in enumerate(questions, start=1):
                    Question.objects.create(
                        quiz=quiz, question_text=text, options=options_,
                        correct_answer=correct, order=order,
                    )
