import axios from "axios";

const api = axios.create({ baseURL: "http://localhost:8000" });

export async function uploadResume(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await api.post("/resume/upload", form);
  return res.data;
}

export async function getJobs() {
  const res = await api.get("/jobs");
  return res.data;
}

export async function matchResume(payload) {
  const res = await api.post("/analysis/match", payload);
  return res.data;
}

export async function recommendJobs(resumeId) {
  const res = await api.get(`/analysis/recommend/${resumeId}`);
  return res.data;
}

export function getErrorMessage(err) {
  if (!err.response) {
    return "Cannot reach the server. Is the backend running on port 8000?";
  }
  const detail = err.response.data?.detail;
  return typeof detail === "string" ? detail : "Something went wrong. Please try again.";
}