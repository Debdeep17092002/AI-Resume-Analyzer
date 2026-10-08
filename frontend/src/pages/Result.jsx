import { useEffect, useState } from "react";
import { Link, Navigate, useLocation } from "react-router-dom";
import ScoreGauge from "../components/ScoreGauge";
import SkillChips from "../components/SkillChips";
import Suggestions from "../components/Suggestions";
import { recommendJobs } from "../services/api";

export default function Result() {
  const { state } = useLocation();
  const [recommended, setRecommended] = useState([]);

  const resumeId = state?.result?.resume_id;

  useEffect(() => {
    if (resumeId) {
      recommendJobs(resumeId).then(setRecommended).catch(() => {});
    }
  }, [resumeId]);

  // If the page was opened directly or refreshed, there is no data
  if (!state) return <Navigate to="/" replace />;

  const { result } = state;

  return (
    <div>
      <Link to="/">← Analyze another</Link>
      <h1>{result.job_title ? `Match for ${result.job_title}` : "Match result"}</h1>

      <section className="card score-row">
        <ScoreGauge score={result.match_score} />
        <div>
          <p>Skill overlap: <strong>{result.skill_overlap}%</strong></p>
          <p>Semantic similarity: <strong>{result.semantic_similarity}</strong></p>
          <p className="muted">
            Overall score = 60% skill overlap + 40% how similar your resume's content is to the job.
          </p>
        </div>
      </section>

      <section className="card">
        <SkillChips title="Matched skills" skills={result.matched_skills} variant="good" />
        <SkillChips title="Missing skills" skills={result.missing_skills} variant="bad" />
      </section>

      {result.suggestions.length > 0 && (
        <section className="card">
          <h2>How to close the gap</h2>
          <Suggestions items={result.suggestions} />
        </section>
      )}

      {result.tips.length > 0 && (
        <section className="card">
          <h2>Resume tips</h2>
          <ul>
            {result.tips.map((tip) => (
              <li key={tip}>{tip}</li>
            ))}
          </ul>
        </section>
      )}

      {recommended.length > 0 && (
        <section className="card">
          <h2>Best matching jobs for you</h2>
          <table>
            <thead>
              <tr><th>Job</th><th>Company</th><th>Score</th></tr>
            </thead>
            <tbody>
              {recommended.map((job) => (
                <tr key={job.job_id}>
                  <td>{job.title}</td>
                  <td>{job.company}</td>
                  <td>{job.match_score}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}
    </div>
  );
}