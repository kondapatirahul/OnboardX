import { useCallback, useEffect, useMemo, useState } from 'react';
import { Activity, Award, BarChart3, CalendarDays, CheckCircle2, CircleAlert, Plus, RefreshCw, Target, Users } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { employeeService } from '../services/employees';
import { performanceService } from '../services/performance';
import '../styles/performance/performance.css';

const emptyGoal = { owner_id: '', title: '', description: '', goal_type: 'individual', priority: 'medium', start_date: '', due_date: '', key_results: [{ title: '', metric: '', start_value: 0, target_value: 100, current_value: 0, weight: 1 }] };
const dateLabel = (value) => value ? new Date(value).toLocaleDateString() : '—';

export default function PerformancePage() {
  const { user } = useAuth();
  const canManage = ['HR_ADMIN', 'SUPER_ADMIN', 'MANAGER'].includes(user?.role);
  const isHR = ['HR_ADMIN', 'SUPER_ADMIN'].includes(user?.role);
  const [tab, setTab] = useState('goals');
  const [goals, setGoals] = useState([]); const [reviews, setReviews] = useState([]); const [cycles, setCycles] = useState([]); const [plans, setPlans] = useState([]); const [people, setPeople] = useState([]); const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true); const [busy, setBusy] = useState(false); const [error, setError] = useState(''); const [notice, setNotice] = useState('');
  const [showGoal, setShowGoal] = useState(false); const [goal, setGoal] = useState(emptyGoal); const [showCycle, setShowCycle] = useState(false);
  const [cycle, setCycle] = useState({ name: '', cycle_type: 'quarterly', starts_at: '', ends_at: '', self_review_deadline: '', manager_review_deadline: '', description: '' });
  const [search, setSearch] = useState('');

  const refresh = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [g, r, c, p] = await Promise.all([performanceService.goals(), performanceService.reviews(), performanceService.cycles(), performanceService.plans()]);
      setGoals(g || []); setReviews(r || []); setCycles(c || []); setPlans(p || []);
      if (isHR) { const [a, e] = await Promise.all([performanceService.analytics(), employeeService.list({ page: 1, page_size: 200, status: 'active' })]); setStats(a); setPeople(e.items || []); }
      else if (user?.role === 'MANAGER') { setPeople(await performanceService.team() || []); }
    } catch (err) { setError(err.message || 'Unable to load performance workspace.'); }
    finally { setLoading(false); }
  }, [isHR, user?.role]);
  useEffect(() => { refresh(); }, [refresh]);

  const visibleGoals = useMemo(() => goals.filter((item) => `${item.title} ${item.employee_name || ''} ${item.description || ''}`.toLowerCase().includes(search.toLowerCase())), [goals, search]);
  const setGoalField = (key, value) => setGoal((old) => ({ ...old, [key]: value }));
  const setKeyField = (index, key, value) => setGoal((old) => ({ ...old, key_results: old.key_results.map((row, i) => i === index ? { ...row, [key]: value } : row) }));

  const submitGoal = async (event) => {
    event.preventDefault(); setBusy(true); setError('');
    try {
      await performanceService.createGoal({ ...goal, start_date: goal.start_date ? new Date(`${goal.start_date}T00:00:00`).toISOString() : null, due_date: goal.due_date ? new Date(`${goal.due_date}T23:59:00`).toISOString() : null, key_results: goal.key_results.filter((row) => row.title.trim()).map((row) => ({ ...row, start_value: Number(row.start_value), target_value: Number(row.target_value), current_value: Number(row.current_value), weight: Number(row.weight) })) });
      setNotice('Goal and key results created.'); setShowGoal(false); setGoal(emptyGoal); await refresh();
    } catch (err) { setError(err.message || 'Could not create goal.'); } finally { setBusy(false); }
  };

  const submitCycle = async (event) => {
    event.preventDefault(); setBusy(true); setError('');
    try { await performanceService.createCycle({ ...cycle, starts_at: new Date(cycle.starts_at).toISOString(), ends_at: new Date(cycle.ends_at).toISOString(), self_review_deadline: cycle.self_review_deadline ? new Date(cycle.self_review_deadline).toISOString() : null, manager_review_deadline: cycle.manager_review_deadline ? new Date(cycle.manager_review_deadline).toISOString() : null }); setNotice('Review cycle created.'); setShowCycle(false); await refresh(); }
    catch (err) { setError(err.message || 'Could not create review cycle.'); } finally { setBusy(false); }
  };

  const startReviews = async (cycleId) => {
    const employeeId = window.prompt('Enter the employee ID to create a review for:');
    if (!employeeId) return;
    try { await performanceService.createReview(cycleId, employeeId.trim()); setNotice('Review created for the employee.'); await refresh(); }
    catch (err) { setError(err.message || 'Could not create review.'); }
  };

  const submitSelf = async (row) => {
    const rating = window.prompt('Self-rating from 1 to 5:'); if (rating === null) return;
    const summary = window.prompt('Summarize your contributions (at least 10 characters):'); if (!summary) return;
    try { await performanceService.selfReview(row.id, { self_rating: Number(rating), self_summary: summary }); setNotice('Self-review submitted.'); await refresh(); }
    catch (err) { setError(err.message || 'Could not submit self-review.'); }
  };

  const submitManager = async (row) => {
    const rating = window.prompt('Manager rating from 1 to 5:'); if (rating === null) return;
    const summary = window.prompt('Manager review summary (at least 10 characters):'); if (!summary) return;
    try { await performanceService.managerReview(row.id, { manager_rating: Number(rating), manager_summary: summary }); setNotice('Manager review submitted.'); await refresh(); }
    catch (err) { setError(err.message || 'Could not submit manager review.'); }
  };

  const cards = isHR ? [{ label: 'Active goals', value: stats?.goals ?? goals.length, icon: Target }, { label: 'Goals completed', value: stats?.goals_completed ?? 0, icon: CheckCircle2 }, { label: 'Reviews pending', value: stats?.reviews_pending ?? reviews.filter((r) => r.status !== 'completed').length, icon: Users }, { label: 'At-risk goals', value: stats?.at_risk_goals ?? 0, icon: CircleAlert }] : [{ label: 'My goals', value: goals.length, icon: Target }, { label: 'Completed', value: goals.filter((g) => g.status === 'completed').length, icon: CheckCircle2 }, { label: 'Reviews', value: reviews.length, icon: Award }, { label: 'Improvement plans', value: plans.length, icon: Activity }];

  return <main className="performance-page">
    <header className="performance-header"><div><span className="performance-eyebrow">PEOPLE DEVELOPMENT</span><h1>Performance & goals</h1><p>Align objectives, track measurable outcomes, and make performance conversations meaningful.</p></div><div className="performance-actions">{canManage && <button className="performance-primary" onClick={() => setShowGoal(true)}><Plus size={16}/> Create goal</button>}{isHR && <button className="performance-secondary" onClick={() => setShowCycle(true)}><CalendarDays size={16}/> New review cycle</button>}</div></header>
    <section className="performance-stats">{cards.map(({ label, value, icon: Icon }) => <article key={label}><span><Icon size={18}/></span><div><strong>{value}</strong><small>{label}</small></div></article>)}</section>
    {error && <div className="performance-alert">{error}<button onClick={() => setError('')}>Dismiss</button></div>}{notice && <div className="performance-notice">{notice}<button onClick={() => setNotice('')}>Dismiss</button></div>}
    <nav className="performance-tabs">{[['goals','Goals & OKRs'],['reviews','Review cycles'],['plans','Improvement plans']].map(([key,label]) => <button key={key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>{label}</button>)}<button className="performance-refresh" onClick={refresh} disabled={loading}><RefreshCw size={15}/></button></nav>
    {loading ? <div className="performance-empty">Loading performance workspace…</div> : <>
      {tab === 'goals' && <><div className="performance-toolbar"><label><span>⌕</span><input value={search} onChange={(e) => setSearch(e.target.value)} placeholder="Search goals or employees"/></label><span>{visibleGoals.length} goals</span></div><div className="performance-goal-grid">{visibleGoals.map((item) => <article className="performance-goal-card" key={item.id}><div className="performance-goal-top"><span className={`performance-priority ${item.priority}`}>{item.priority}</span><span className={`performance-state ${item.status}`}>{item.status.replace('_',' ')}</span></div><h2>{item.title}</h2><p>{item.description || 'No additional description provided.'}</p><div className="performance-owner">{item.employee_name || 'Your goal'} <span>Due {dateLabel(item.due_date)}</span></div><div className="performance-progress"><span style={{ width: `${item.progress || 0}%` }}/></div><div className="performance-progress-label"><strong>{item.progress || 0}%</strong><small>weighted progress</small></div>{item.key_results?.length > 0 && <div className="performance-key-results">{item.key_results.map((kr) => <div key={kr.id}><span>{kr.title}</span><small>{kr.current_value} / {kr.target_value} {kr.metric || ''}</small><div><i style={{ width: `${kr.progress}%` }}/></div></div>)}</div>}</article>)}{!visibleGoals.length && <div className="performance-empty">No goals found. {canManage ? 'Create the first goal to get started.' : 'Your goals will appear here once assigned.'}</div>}</div></>}
      {tab === 'reviews' && <section className="performance-panel"><div className="performance-panel-heading"><div><h2>Review cycles</h2><p>Review windows and employee feedback progress</p></div></div>{cycles.map((item) => <article className="performance-cycle-row" key={item.id}><div><strong>{item.name}</strong><small>{item.cycle_type} · {dateLabel(item.starts_at)} – {dateLabel(item.ends_at)}</small></div><span className={`performance-state ${item.status}`}>{item.status}</span>{canManage && <button onClick={() => startReviews(item.id)}>Create review</button>}</article>)}{!cycles.length && <div className="performance-empty">No review cycles have been scheduled.</div>}<div className="performance-panel-heading review-heading"><div><h2>Employee reviews</h2><p>Self-assessments and manager evaluations</p></div></div>{reviews.map((row) => <article className="performance-review-row" key={row.id}><div><strong>{row.employee_name}</strong><small>Self: {row.self_rating ?? 'Pending'} / 5 · Manager: {row.manager_rating ?? 'Pending'} / 5</small></div><span className={`performance-state ${row.status}`}>{row.status.replace('_',' ')}</span>{row.status !== 'completed' && <div className="performance-review-actions">{row.status === 'not_started' && <button onClick={() => submitSelf(row)}>Self review</button>}{canManage && <button onClick={() => submitManager(row)}>Manager review</button>}</div>}</article>)}{!reviews.length && <div className="performance-empty">No reviews assigned yet.</div>}</section>}
      {tab === 'plans' && <section className="performance-panel"><div className="performance-panel-heading"><div><h2>Performance improvement plans</h2><p>Structured objectives, support and follow-up windows</p></div></div>{plans.map((plan) => <article className="performance-plan-row" key={plan.id}><div><strong>{plan.title}</strong><small>{plan.employee_name} · {dateLabel(plan.starts_at)} – {dateLabel(plan.ends_at)}</small><p>{plan.objectives}</p></div><span className={`performance-state ${plan.status}`}>{plan.status}</span></article>)}{!plans.length && <div className="performance-empty">No improvement plans recorded.</div>}</section>}
    </>}
    {showGoal && <div className="performance-overlay"><form className="performance-modal" onSubmit={submitGoal}><header><div><span className="performance-eyebrow">OBJECTIVE BUILDER</span><h2>Create a measurable goal</h2></div><button type="button" onClick={() => setShowGoal(false)}>×</button></header><div className="performance-form-grid"><label className="wide">Goal title<input required minLength="3" value={goal.title} onChange={(e) => setGoalField('title',e.target.value)} placeholder="Improve customer response time"/></label><label className="wide">Description<textarea value={goal.description} onChange={(e) => setGoalField('description',e.target.value)} rows="3"/></label><label>Employee<select required value={goal.owner_id} onChange={(e) => setGoalField('owner_id',e.target.value)}><option value="">Select employee</option>{people.map((p) => <option key={p.id} value={p.id}>{p.full_name || p.name || p.email}</option>)}</select></label><label>Priority<select value={goal.priority} onChange={(e) => setGoalField('priority',e.target.value)}><option value="low">Low</option><option value="medium">Medium</option><option value="high">High</option><option value="critical">Critical</option></select></label><label>Start date<input type="date" value={goal.start_date} onChange={(e) => setGoalField('start_date',e.target.value)}/></label><label>Due date<input type="date" value={goal.due_date} onChange={(e) => setGoalField('due_date',e.target.value)}/></label></div><div className="performance-kr-builder"><div><strong>Key results</strong><button type="button" onClick={() => setGoal((old) => ({ ...old, key_results: [...old.key_results, { title: '', metric: '', start_value: 0, target_value: 100, current_value: 0, weight: 1 }] }))}><Plus size={13}/> Add result</button></div>{goal.key_results.map((kr,index) => <div className="performance-kr-fields" key={index}><label>Result title<input value={kr.title} onChange={(e) => setKeyField(index,'title',e.target.value)} placeholder="Complete 20 customer interviews"/></label><label>Metric<input value={kr.metric} onChange={(e) => setKeyField(index,'metric',e.target.value)} placeholder="interviews"/></label><label>Target<input type="number" value={kr.target_value} onChange={(e) => setKeyField(index,'target_value',e.target.value)}/></label><label>Weight<input type="number" min="0.1" step="0.1" value={kr.weight} onChange={(e) => setKeyField(index,'weight',e.target.value)}/></label></div>)}</div><footer><button type="button" className="performance-secondary" onClick={() => setShowGoal(false)}>Cancel</button><button className="performance-primary" disabled={busy}>{busy ? 'Saving…' : 'Create goal'}</button></footer></form></div>}
    {showCycle && <div className="performance-overlay"><form className="performance-modal" onSubmit={submitCycle}><header><div><span className="performance-eyebrow">REVIEW SCHEDULE</span><h2>Create review cycle</h2></div><button type="button" onClick={() => setShowCycle(false)}>×</button></header><div className="performance-form-grid"><label className="wide">Cycle name<input required value={cycle.name} onChange={(e) => setCycle({...cycle,name:e.target.value})} placeholder="Q4 2026 performance review"/></label><label>Type<select value={cycle.cycle_type} onChange={(e) => setCycle({...cycle,cycle_type:e.target.value})}><option value="quarterly">Quarterly</option><option value="half_yearly">Half-yearly</option><option value="annual">Annual</option><option value="probation">Probation</option></select></label><label>Starts<input required type="datetime-local" value={cycle.starts_at} onChange={(e) => setCycle({...cycle,starts_at:e.target.value})}/></label><label>Ends<input required type="datetime-local" value={cycle.ends_at} onChange={(e) => setCycle({...cycle,ends_at:e.target.value})}/></label><label>Self-review deadline<input type="datetime-local" value={cycle.self_review_deadline} onChange={(e) => setCycle({...cycle,self_review_deadline:e.target.value})}/></label><label className="wide">Description<textarea value={cycle.description} onChange={(e) => setCycle({...cycle,description:e.target.value})}/></label></div><footer><button type="button" className="performance-secondary" onClick={() => setShowCycle(false)}>Cancel</button><button className="performance-primary" disabled={busy}>{busy ? 'Saving…' : 'Create cycle'}</button></footer></form></div>}
  </main>;
}
