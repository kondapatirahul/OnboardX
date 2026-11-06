import { useState } from 'react';
import { UserPlus } from 'lucide-react';

export default function AssignmentForm({ employees, templates, onAssign, saving }) {
  const [employeeId, setEmployeeId] = useState('');
  const [templateId, setTemplateId] = useState('');
  const activeTemplates = templates.filter((template) => template.is_active);
  const submit = async (event) => { event.preventDefault(); if (!employeeId || !templateId) return; const done = await onAssign({ employee_id: employeeId, template_id: templateId }); if (done) { setEmployeeId(''); setTemplateId(''); } };
  return <form className="onboard-assignment" onSubmit={submit}><div className="onboard-assignment-intro"><span className="onboard-template-icon"><UserPlus size={17} /></span><div><strong>Assign onboarding</strong><p>Start a workflow for an employee.</p></div></div><label>Employee<select required value={employeeId} onChange={(event) => setEmployeeId(event.target.value)}><option value="">Select employee</option>{employees.map((employee) => <option key={employee.id} value={employee.id}>{employee.full_name} · {employee.employee_id}</option>)}</select></label><label>Template<select required value={templateId} onChange={(event) => setTemplateId(event.target.value)}><option value="">Select active template</option>{activeTemplates.map((template) => <option key={template.id} value={template.id}>{template.name}</option>)}</select></label><button type="submit" className="onboard-btn onboard-btn--primary" disabled={saving || !employees.length || !activeTemplates.length}>{saving ? 'Assigning…' : 'Assign workflow'}</button>{!activeTemplates.length && <small>Create or activate a template before assigning.</small>}</form>;
}
