from django.core.management.base import BaseCommand

from courses.models import Course, Lesson

COURSES = [
    ("HTML & CSS Foundations", "Beginner", 2, "Personal portfolio page",
     "Build and style responsive web pages from scratch using semantic HTML, Flexbox and Grid.",
     ["Structure pages with semantic HTML", "Style layouts with Flexbox and Grid", "Make pages mobile-friendly"],
     ["Intro to HTML", "Text, links and images", "Semantic layout", "CSS selectors", "Flexbox", "Grid", "Responsive design"]),
    ("JavaScript Fundamentals", "Beginner", 3, "To-do list app",
     "Learn variables, functions, arrays, objects and the DOM by building small interactive tools.",
     ["Write and debug JavaScript", "Handle events and update the DOM", "Fetch data from an API"],
     ["Variables and types", "Functions", "Arrays and objects", "The DOM", "Events", "Fetch API"]),
    ("Python Basics", "Beginner", 3, "Command-line expense tracker",
     "Start programming with Python: data types, control flow, functions and simple classes.",
     ["Write clear Python functions", "Work with lists and dictionaries", "Read and write files"],
     ["Hello Python", "Data types", "Control flow", "Functions", "Lists and dictionaries", "Files", "Classes"]),
    ("SQL Basics", "Intermediate", 2, "Library database",
     "Design tables and query data with SELECT, JOIN, GROUP BY and constraints.",
     ["Design relational tables", "Join and aggregate data", "Use keys and constraints"],
     ["Tables and keys", "SELECT", "Filtering", "JOIN", "GROUP BY"]),
    ("Beginner Web Projects", "Intermediate", 3, "Weather dashboard",
     "Combine HTML, CSS and JavaScript into complete projects you can publish on GitHub.",
     ["Plan a small project", "Use Git and GitHub", "Deploy a static site"],
     ["Plan the project", "Git and GitHub", "Build the UI", "Connect an API", "Deploy"]),
]


class Command(BaseCommand):
    help = "Load the sample courses (safe to run more than once)."

    def handle(self, *args, **options):
        for title, level, weeks, project, desc, outcomes, lessons in COURSES:
            course, created = Course.objects.get_or_create(
                title=title,
                defaults=dict(level=level, weeks=weeks, project=project,
                              description=desc, outcomes=outcomes, published=True),
            )
            if created:
                for number, lesson_title in enumerate(lessons, start=1):
                    Lesson.objects.create(course=course, title=lesson_title, sequence_number=number)
                self.stdout.write(f"Added: {title}")
            else:
                self.stdout.write(f"Already exists: {title}")
