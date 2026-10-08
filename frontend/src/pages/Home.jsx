import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import FileUploader from "../components/FileUploader";
import SkillChips from "../components/SkillChips";
import { getErrorMessage, getJobs, matchResume, uploadResume } from "../services/api";

export default function Home() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [resume, setResume] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [mode, setMode] = useState("select");
  const [jobId, setJobId] = useState("");
  const [jobDescription, setJobDescription] = useState("");
  const [uploading, setUploading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getJobs()
      .then((data) => {
        setJobs(data);
        if (data.length > 0) setJobId(String(data[0].id));
      })
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  function handleFile(f) {
    setFile(f);
    setResume(null);
    setError("");
  }

  async function handleUpload() {
    setUploading(true);
    setError("");
    try {
      setResume(await uploadResume(file));
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUploading(false);
    }
  }

  async function handleAnalyze() {
    setAnalyzing(true);
    setError("");
    try {
      const payload =
        mode === "select"
          ? { resume_id: resume.id, job_id: Number(jobId) }
          : { resume_id: resume.id, job_description: jobDescription };
      const result = await matchResume(payload);
      navigate("/result", { state: { result, resume } });
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setAnalyzing(false);
    }
  }

  const canAnalyze =
    resume && (mode === "select" ? jobId : jobDescription.trim().length > 20);

  return (
    <div>
      <h1>Analyze your resume</h1>
      <p className="muted">Upload your resume, choose a job, and see how well you match.</p>

      {error && <div className="error">{error}</div>}

      <section className="card">
        <h2>1. Upload your resume</h2>
        <FileUploader file={file} onFile={handleFile} />
        <button className="btn" disabled={!file || uploading} onClick={handleUpload}>
          {uploading ? "Reading resume..." : "Upload and read"}
        </button>

        {resume && (
          <div className="parsed">
            <p>
              <strong>{resume.name || "Name not found"}</strong>
              {resume.email && <> · {resume.email}</>}
              {resume.phone && <> · {resume.phone}</>}
            </p>
            <SkillChips title="Skills found" skills={resume.skills} variant="good" />
          </div>
        )}
      </section>

      {resume && (
        <section className="card">
          <h2>2. Choose a job</h2>
          <div className="tabs">
            <button
              className={mode === "select" ? "tab active" : "tab"}
              onClick={() => setMode("select")}
            >
              Pick from list
            </button>
            <button
              className={mode === "paste" ? "tab active" : "tab"}
              onClick={() => setMode("paste")}
            >
              Paste job description
            </button>
          </div>

          {mode === "select" ? (
            <select value={jobId} onChange={(e) => setJobId(e.target.value)}>
              {jobs.map((j) => (
                <option key={j.id} value={j.id}>
                  {j.title} ({j.company})
                </option>
              ))}
            </select>
          ) : (
            <textarea
              rows={8}
              placeholder="Paste the full job description here..."
              value={jobDescription}
              onChange={(e) => setJobDescription(e.target.value)}
            />
          )}

          <button className="btn" disabled={!canAnalyze || analyzing} onClick={handleAnalyze}>
            {analyzing ? "Analyzing... (first time can take a while)" : "Analyze match"}
          </button>
        </section>
      )}
    </div>
  );
}