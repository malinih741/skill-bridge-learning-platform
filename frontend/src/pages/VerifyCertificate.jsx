import { Link, useParams } from "react-router-dom";
import Status from "../components/Status.jsx";
import useFetch from "../hooks/useFetch.js";
import { verifyCertificate } from "../services/api.js";

const formatDate = (iso) =>
  new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "long", day: "numeric" });

export default function VerifyCertificate() {
  const { number } = useParams();
  const { data, loading, error } = useFetch(() => verifyCertificate(number), [number]);

  if (loading) {
    return <section className="container section"><Status loading /></section>;
  }

  if (error && error.status === 404) {
    return (
      <section className="container section narrow">
        <h1>Certificate not found</h1>
        <p className="status status-error" role="alert">
          No certificate matches “{number}”. Check the number and try again.
        </p>
        <Link to="/verify" className="btn">Try another number</Link>
      </section>
    );
  }

  if (error) {
    return <section className="container section"><Status error={error} /></section>;
  }

  if (!data.valid) {
    return (
      <section className="container section narrow">
        <h1>Certificate not valid</h1>
        <p className="status status-error" role="alert">{data.detail}</p>
      </section>
    );
  }

  return (
    <section className="container section">
      <p className="success no-print">Verified. This certificate is genuine.</p>
      <article className="certificate">
        <p className="cert-brand">SkillBridge</p>
        <h1>Certificate of Completion</h1>
        <p>This certifies that</p>
        <p className="cert-name">{data.recipient_name}</p>
        <p>has completed the {data.level.toLowerCase()} course</p>
        <p className="cert-course">{data.course_title}</p>
        <p>including all lessons, quizzes and a reviewed final project.</p>
        <p className="meta">
          Issued {formatDate(data.issued_at)} · Certificate number {data.certificate_number}
        </p>
      </article>
      <p className="no-print">
        <button className="btn btn-outline" onClick={() => window.print()}>Print or save as PDF</button>
      </p>
    </section>
  );
}
