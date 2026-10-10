// All backend calls go through here.
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
const TOKEN_KEY = "skillbridge_token";

export function getToken() {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token) {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable: user simply has to log in again next visit */
  }
}

export async function request(path, options = {}, allowRetry = true) {
  const token = getToken();
  const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
  if (token) headers.Authorization = `Token ${token}`;

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  // Old/invalid token: forget it and try once more as a visitor.
  if (response.status === 401 && token && allowRetry) {
    setToken(null);
    return request(path, options, false);
  }

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    let message = body.detail;
    if (!message) {
      const first = Object.values(body)[0];
      message = Array.isArray(first) ? first[0] : `Request failed (${response.status})`;
    }
    const error = new Error(message);
    error.status = response.status;
    error.fields = body;
    throw error;
  }

  if (response.status === 204) return null;
  return response.json();
}

const post = (path, data) => request(path, { method: "POST", body: JSON.stringify(data || {}) });

// Courses
export const getCourses = () => request("/courses/");
export const getCourse = (id) => request(`/courses/${id}/`);
export const enroll = (id) => post(`/courses/${id}/enroll/`);
export const getMyCourses = () => request("/my-courses/");

// Auth
export const register = (name, email, password) => post("/auth/register/", { name, email, password });
export const login = (email, password) => post("/auth/login/", { email, password });
export const logout = () => post("/auth/logout/");
export const getMe = () => request("/auth/me/");

// Learning
export const getCourseLessons = (courseId) => request(`/courses/${courseId}/lessons/`);
export const completeLesson = (lessonId) => post(`/lessons/${lessonId}/complete/`);
export const getCourseQuizzes = (courseId) => request(`/courses/${courseId}/quizzes/`);
export const submitQuiz = (quizId, answers) => post(`/quizzes/${quizId}/submit/`, { answers });

// Project + certificate
export const getProgress = (courseId) => request(`/courses/${courseId}/progress/`);
export const submitProject = (courseId, data) => post(`/courses/${courseId}/project/`, data);
export const getMyCertificates = () => request("/my-certificates/");
export const verifyCertificate = (number) =>
  request(`/certificates/verify/${encodeURIComponent(number)}/`);
