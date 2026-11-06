import { useState } from 'react';
import { Plus, Trash2, X } from 'lucide-react';

export default function TemplateForm({ onClose, onSubmit, saving, error }) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [stages, setStages] = useState([{ name: 'Welcome and orientation', description: '', duration_days: 1 }]);

  const updateStage = (index, field, value) => setStages((current) => current.map((stage, i) => i === index ? { ...stage, [field]: value } : stage));
  const addStage = () => setStages((current) => current.length >= 50 ? current : [...current, { name: '', description: '', duration_days: 1 }]);
  const removeStage = (index) => setStages((current) => current.filter((_, i) => i !== index));
  const submit = (event) => {
    event.preventDefault();
    onSubmit({ name: name.trim(), description: description.trim() || null, stages: stages.map((stage, order_index) => ({ name: stage.name.trim(), description: stage.description.trim() || null, order_index, duration_days: Number(stage.duration_days) || null })) });
  };

  return <div className="onboard-modal-backdrop" role="presentation"><section className="onboard-modal" role="dialog" aria-modal="true" aria-labelledby="template-title">
    <header className="onboard-modal-head"><div><span className="onboard-eyebrow">WORKFLOW DESIGN</span><h2 id="template-title">Create onboarding template</h2><p>Define the stages a new employee will complete.</p></div><button className="onboard-icon-btn" type="button" onClick={onClose} aria-label="Close"><X size={18} /></button></header>
    <form className="onboard-form" onSubmit={submit}>
      <label>Template name<input required minLength="2" maxLength="255" value={name} onChange={(event) => setName(event.target.value)} placeholder="e.g. Standard employee onboarding" /></label>
      <label>Description<textarea rows="2" value={description} onChange={(event) => setDescription(event.target.value)} placeholder="What this workflow covers" /></label>
      <div className="onboard-stage-heading"><div><strong>Stages</strong><span>{stages.length} of 50</span></div><button type="button" className="onboard-btn onboard-btn--light" onClick={addStage} disabled={stages.length >= 50}><Plus size={14} /> Add stage</button></div>
      <div className="onboard-stage-list">{stages.map((stage, index) => <div className="onboard-stage-editor" key={index}><div className="onboard-stage-number">{index + 1}</div><div className="onboard-stage-fields"><input required minLength="2" value={stage.name} onChange={(event) => updateStage(index, 'name', event.target.value)} placeholder="Stage name" aria-label={`Stage ${index + 1} name`} /><input value={stage.description} onChange={(event) => updateStage(index, 'description', event.target.value)} placeholder="Description (optional)" aria-label={`Stage ${index + 1} description`} /><label>Days<input type="number" min="1" max="3650" value={stage.duration_days} onChange={(event) => updateStage(index, 'duration_days', event.target.value)} /></label></div><button type="button" className="onboard-icon-btn onboard-danger" onClick={() => removeStage(index)} disabled={stages.length === 1} aria-label={`Remove stage ${index + 1}`}><Trash2 size={15} /></button></div>)}</div>
      {error && <p className="onboard-form-error" role="alert">{error}</p>}
      <footer className="onboard-form-actions"><button type="button" className="onboard-btn onboard-btn--light" onClick={onClose}>Cancel</button><button type="submit" className="onboard-btn onboard-btn--primary" disabled={saving}>{saving ? 'Saving…' : 'Create template'}</button></footer>
    </form>
  </section></div>;
}
