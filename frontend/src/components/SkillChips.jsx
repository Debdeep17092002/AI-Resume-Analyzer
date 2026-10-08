export default function SkillChips({ title, skills, variant = "neutral" }) {
  return (
    <div className="chips-block">
      {title && <h3>{title}</h3>}
      {skills.length === 0 ? (
        <p className="muted">None</p>
      ) : (
        <div className="chips">
          {skills.map((s) => (
            <span key={s} className={`chip ${variant}`}>{s}</span>
          ))}
        </div>
      )}
    </div>
  );
}