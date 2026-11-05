import '../styles/layout.css';

export default function PlaceholderPage({ title }) {
  return (
    <div>
      <div className="page-header">
        <div>
          <h1>{title}</h1>
          <p>This module is under development.</p>
        </div>
      </div>
      <div className="card">
        <div className="empty-state">
          <p>Coming soon — {title} module will be available shortly.</p>
        </div>
      </div>
    </div>
  );
}
