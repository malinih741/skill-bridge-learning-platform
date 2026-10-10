// Shared loading / error message.
export default function Status({ loading, error }) {
  if (loading) return <p className="status">Loading courses…</p>;
  if (error) {
    return (
      <p className="status status-error" role="alert">
        Couldn't load data. Make sure the backend is running at http://localhost:8000, then refresh.
      </p>
    );
  }
  return null;
}
