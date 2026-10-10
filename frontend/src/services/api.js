// All backend calls go through here.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    const error = new Error(body.detail || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }
  return response.json();
}

export const getCourses = () => request("/courses/");
export const getCourse = (id) => request(`/courses/${id}/`);
