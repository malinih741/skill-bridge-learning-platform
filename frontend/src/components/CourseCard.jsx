import { Link } from "react-router-dom";

export default function CourseCard({ course }) {
  return (
    <article className="course-card">
      <span className={`badge badge-${course.level.toLowerCase()}`}>{course.level}</span>
      <h3>{course.title}</h3>
      <p>{course.description}</p>
      <p className="meta">{course.lessons} lessons · {course.weeks} weeks</p>
      <Link to={`/courses/${course.id}`} className="btn btn-outline">View course</Link>
    </article>
  );
}
