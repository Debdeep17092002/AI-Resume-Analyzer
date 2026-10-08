export default function Suggestions({ items }) {
  if (!items || items.length === 0) return null;

  return (
    <ul className="suggestions">
      {items.map((item) => (
        <li key={item.skill}>
          Learn <strong>{item.skill}</strong>:{" "}
          <a href={item.resource} target="_blank" rel="noreferrer">
            open resource
          </a>
        </li>
      ))}
    </ul>
  );
}