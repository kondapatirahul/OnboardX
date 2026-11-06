import { useEffect, useState } from 'react';
import { AlertCircle, ClipboardCheck, Layers3, Plus, RefreshCw } from 'lucide-react';
import { employeeService } from '../services/employees';
import { onboardingService } from '../services/onboarding';
import { useOnboarding } from '../hooks/useOnboarding';
import TemplateForm from '../components/onboarding/TemplateForm';
import TemplateList from '../components/onboarding/TemplateList';
import AssignmentForm from '../components/onboarding/AssignmentForm';
import ProgressList from '../components/onboarding/ProgressList';
import '../styles/onboarding/onboarding.css';

export default function OnboardingPage() {
  const { templates, instances, loading, error, refresh } = useOnboarding();
  const [employees, setEmployees] = useState([]);
  const [employeeError, setEmployeeError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [saving, setSaving] = useState(false);
  const [actionError, setActionError] = useState('');
  const [notice, setNotice] = useState('');

  const loadEmployees = async () => {
    try { const result = await employeeService.list({ page: 1, page_size: 100, status: 'active' }); setEmployees(result.items || []); setEmployeeError(''); }
    catch (err) { setEmployeeError(err.message || 'Unable to load employees.'); }
  };
  useEffect(() => { loadEmployees(); }, []);

  const runAction = async (action, successMessage) => {
    setSaving(true); setActionError(''); setNotice('');
    try { await action(); setNotice(successMessage); await refresh(); return true; }
    catch (err) { setActionError(err.message || 'The action could not be completed.'); return false; }
    finally { setSaving(false); }
  };
  const createTemplate = async (payload) => { const done = await runAction(() => onboardingService.createTemplate(payload), 'Onboarding template created.'); if (done) setShowForm(false); };
  const toggleTemplate = (template) => runAction(() => onboardingService.updateTemplate(template.id, { is_active: !template.is_active }), `Template ${template.is_active ? 'deactivated' : 'activated'}.`);
  const assign = (payload) => runAction(() => onboardingService.assign(payload), 'Onboarding workflow assigned.');
  const updateTask = (instanceId, taskId, status) => runAction(() => onboardingService.updateTask(instanceId, taskId, status), 'Task status updated.');

  return <section className="onboarding-page">
    <header className="onboarding-header"><div><span className="onboard-eyebrow">PEOPLE OPERATIONS</span><h1>Onboarding</h1><p>Build consistent employee journeys and track every onboarding task.</p></div><button type="button" className="onboard-btn onboard-btn--primary" onClick={() => setShowForm(true)}><Plus size={16} /> Create template</button></header>
    <div className="onboard-summary-grid"><article><span className="onboard-summary-icon"><Layers3 size={18} /></span><div><strong>{templates.length}</strong><small>Templates</small></div></article><article><span className="onboard-summary-icon coral"><ClipboardCheck size={18} /></span><div><strong>{instances.filter((item) => item.status !== 'completed').length}</strong><small>Active journeys</small></div></article><article><span className="onboard-summary-icon"><ClipboardCheck size={18} /></span><div><strong>{instances.filter((item) => item.status === 'completed').length}</strong><small>Completed journeys</small></div></article></div>
    {(error || actionError || employeeError) && <div className="onboard-alert" role="alert"><AlertCircle size={16} /><span>{error || actionError || employeeError}</span><button type="button" onClick={() => { refresh(); loadEmployees(); }}>Retry</button></div>}
    {notice && <div className="onboard-notice" role="status">{notice}</div>}
    <div className="onboard-section-heading"><div><h2>Workflow templates</h2><p>Reusable onboarding plans for your organization.</p></div><button type="button" className="onboard-refresh" onClick={() => { refresh(); loadEmployees(); }} disabled={loading}><RefreshCw size={14} /> Refresh</button></div>
    {loading ? <div className="onboard-loading">Loading onboarding data…</div> : <TemplateList templates={templates} onToggle={toggleTemplate} />}
    <div className="onboard-lower-grid"><section className="onboard-panel"><div className="onboard-section-heading"><div><h2>Assign a workflow</h2><p>Choose an employee and an active template.</p></div></div><AssignmentForm employees={employees} templates={templates} onAssign={assign} saving={saving} /></section><section className="onboard-panel"><div className="onboard-section-heading"><div><h2>Onboarding progress</h2><p>Track task completion across active journeys.</p></div></div><ProgressList instances={instances} employees={employees} templates={templates} onTaskStatus={updateTask} /></section></div>
    {showForm && <TemplateForm onClose={() => setShowForm(false)} onSubmit={createTemplate} saving={saving} error={actionError} />}
  </section>;
}
