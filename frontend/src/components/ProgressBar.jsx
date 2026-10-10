export default function ProgressBar({ done, total }) {
  const percent = total ? Math.round((done / total) * 100) : 0;
  return (
    <div>
      <div className="progress" role="progressbar" aria-valuenow={percent} aria-valuemin="0" aria-valuemax="100">
        <div className="progress-fill" style={{ width: `${percent}%` }} />
      </div>
      <p className="meta">{done} of {total} lessons done ({percent}%)</p>
    </div>
  );
}
