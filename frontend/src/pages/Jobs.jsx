import { useEffect, useState } from "react";
import SkillChips from "../components/SkillChips";
import { getErrorMessage, getJobs } from "../services/api";

export default function Jobs() {
  const [jobs, setJobs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getJobs()
      .then(setJobs)
      .catch((err) => setError(getErrorMessage(err)));
  }, []);

  return (
    <div>
      <h1>Jobs</h1>
      {error && <div className="error">{error}</div>}
      {jobs.map((job) => (
        <section key={job.id} className="card">
          <h2>{job.title}</h2>
          <p className="muted">{job.company}</p>
          <p>{job.description}</p>
          <SkillChips skills={job.required_skills} />
        </section>
      ))}
    </div>
  );
}