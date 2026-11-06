import { useCallback, useEffect, useMemo, useState } from 'react';
import { Award, BookOpen, CheckCircle2, Clock3, GraduationCap, Layers3, Plus, RefreshCw, Search, Users, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { employeeService } from '../services/employees';
import { trainingService } from '../services/training';
import '../styles/training/training.css';

const blankCourse = { title: '', description: '', category: 'General', level: 'beginner', duration_minutes: 30, is_mandatory: false, published: false, lessons: [{ title: 'Introduction', description: '', content: '', duration_minutes: 10, order_index: 0, is_preview: true }] };
const formatDate = (value) => value ? new Date(value).toLocaleDateString() : 'No due date';

export default function TrainingPage() {
  const { user } = useAuth();
  const canManage = ['HR_ADMIN', 'SUPER_ADMIN'].includes(user?.role);
  const [tab, setTab] = useState(canManage ? 'catalog' : 'learning');
  const [courses, setCourses] = useState([]);
  const [assignments, setAssignments] = useState([]);
  const [employees, setEmployees] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [certificates, setCertificates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('all');
  const [showCreate, setShowCreate] = useState(false);
  const [courseForm, setCourseForm] = useState(blankCourse);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [selectedAssignment, setSelectedAssignment] = useState(null);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [dueDate, setDueDate] = useState('');
  const [saving, setSaving] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true); setError('');
    try {
      const [courseRows, myRows, certificateRows] = await Promise.all([
        trainingService.courses(), trainingService.myLearning(), trainingService.certificates(),
      ]);
      setCourses(courseRows || []); setAssignments(myRows || []); setCertificates(certificateRows || []);
      if (canManage) {
        const [people, stats, allAssignments] = await Promise.all([
          employeeService.list({ page: 1, page_size: 200, status: 'active' }),
          trainingService.analytics(), trainingService.assignments(),
        ]);
        setEmployees(people.items || []); setAnalytics(stats); setAssignments(allAssignments || []);
      }
    } catch (err) { setError(err.message || 'Unable to load training data.'); }
    finally { setLoading(false); }
  }, [canManage]);

  useEffect(() => { refresh(); }, [refresh]);
  const categories = useMemo(() => ['all', ...new Set(courses.map((item) => item.category || 'General'))], [courses]);
  const filtered = courses.filter((item) => (category === 'all' || (item.category || 'General') === category)
    && `${item.title} ${item.description || ''} ${item.category || ''}`.toLowerCase().includes(search.toLowerCase()));
  const updateField = (key, value) => setCourseForm((current) => ({ ...current, [key]: value }));
  const updateLesson = (index, key, value) => setCourseForm((current) => ({ ...current, lessons: current.lessons.map((lesson, i) => i === index ? { ...lesson, [key]: value } : lesson) }));

  const createCourse = async (event) => {
    event.preventDefault(); setSaving(true); setError('');
    try {
      await trainingService.createCourse({ ...courseForm, duration_minutes: Number(courseForm.duration_minutes), lessons: courseForm.lessons.map((lesson, index) => ({ ...lesson, duration_minutes: Number(lesson.duration_minutes), order_index: index })) });
      setNotice('Course created successfully.'); setShowCreate(false); setCourseForm(blankCourse); await refresh();
    } catch (err) { setError(err.message || 'Unable to create course.'); }
    finally { setSaving(false); }
  };

  const publishCourse = async (course) => {
    try { await trainingService.updateCourse(course.id, { published: !course.published }); setNotice(course.published ? 'Course unpublished.' : 'Course published to the learning catalog.'); await refresh(); }
    catch (err) { setError(err.message); }
  };

  const assignCourse = async () => {
    if (!selectedCourse || !selectedEmployees.length) return;
    setSaving(true); setError('');
    try {
      await trainingService.assign(selectedCourse.id, { employee_ids: selectedEmployees, due_date: dueDate ? new Date(`${dueDate}T23:59:00`).toISOString() : null });
      setNotice('Training assignment created. Existing assignments were left unchanged.'); setSelectedCourse(null); setSelectedEmployees([]); setDueDate(''); await refresh();
    } catch (err) { setError(err.message); }
    finally { setSaving(false); }
  };

  const openLearning = async (assignment) => {
    try { const detail = await trainingService.learningDetail(assignment.id); setSelectedAssignment(detail); }
    catch (err) { setError(err.message); }
  };

  const markLesson = async (lesson) => {
    try {
      const updated = await trainingService.updateLesson(selectedAssignment.id, lesson.id, !lesson.completed);
      const detail = await trainingService.learningDetail(selectedAssignment.id);
      setSelectedAssignment(detail); setNotice(updated.certificate_code ? `Course completed. Certificate ${updated.certificate_code} issued.` : 'Lesson progress saved.'); await refresh();
    } catch (err) { setError(err.message); }
  };

  const statCards = canManage ? [
    { label: 'Courses', value: analytics?.courses ?? courses.length, icon: BookOpen },
    { label: 'Assigned learners', value: analytics?.assignments ?? assignments.length, icon: Users },
    { label: 'Completed', value: analytics?.completed ?? 0, icon: CheckCircle2 },
    { label: 'Completion rate', value: `${analytics?.completion_rate ?? 0}%`, icon: Award },
  ] : [
    { label: 'My courses', value: assignments.length, icon: BookOpen },
    { label: 'In progress', value: assignments.filter((item) => item.status !== 'completed').length, icon: Clock3 },
    { label: 'Completed', value: assignments.filter((item) => item.status === 'completed').length, icon: CheckCircle2 },
    { label: 'Certificates', value: certificates.length, icon: Award },
  ];

  return <section className="training-page">
    <header className="training-header"><div><span className="training-eyebrow">LEARNING & DEVELOPMENT</span><h1>Training center</h1><p>Build skills, deliver learning paths, and measure development across your organization.</p></div>{canManage && <button className="training-primary" onClick={() => setShowCreate(true)}><Plus size={16}/> Create course</button>}</header>
    <div className="training-stats">{statCards.map(({ label, value, icon: Icon }) => <article key={label}><span><Icon size={18}/></span><div><strong>{value}</strong><small>{label}</small></div></article>)}</div>
    {error && <div className="training-alert" role="alert">{error}<button onClick={() => setError('')}><X size={14}/></button></div>}
    {notice && <div className="training-notice" role="status">{notice}<button onClick={() => setNotice('')}><X size={14}/></button></div>}
    <nav className="training-tabs">{(canManage ? [['catalog', 'Course catalog'], ['assignments', 'Assignments'], ['certificates', 'Certificates']] : [['learning', 'My learning'], ['certificates', 'Certificates']]).map(([key, label]) => <button key={key} className={tab === key ? 'active' : ''} onClick={() => setTab(key)}>{label}</button>)}<button className="training-refresh" onClick={refresh} disabled={loading}><RefreshCw size={14}/></button></nav>
    {loading ? <div className="training-empty">Loading learning workspace…</div> : <>
      {(tab === 'catalog' || tab === 'learning') && <>
        <div className="training-toolbar"><label><Search size={15}/><input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Search courses, topics, skills…"/></label><select value={category} onChange={(event) => setCategory(event.target.value)}>{categories.map((item) => <option key={item} value={item}>{item === 'all' ? 'All categories' : item}</option>)}</select></div>
        <div className="training-course-grid">{filtered.map((course) => <article className="training-course-card" key={course.id}><div className="training-course-art"><span><GraduationCap size={25}/></span><small>{course.category || 'General'}</small></div><div className="training-course-body"><div className="training-course-meta"><span>{course.level}</span><span>{course.duration_minutes || 0} min</span></div><h2>{course.title}</h2><p>{course.description || 'A structured learning experience designed to build practical workplace skills.'}</p><div className="training-course-footer"><span><Layers3 size={13}/> {course.lessons?.length || 0} lessons</span>{canManage ? <button onClick={() => publishCourse(course)}>{course.published ? 'Unpublish' : 'Publish'}</button> : <span className="training-tag">Available</span>}</div>{canManage && course.published && <button className="training-outline wide" onClick={() => setSelectedCourse(course)}>Assign to employees</button>}</div></article>)}{!filtered.length && <div className="training-empty">No courses match your search.</div>}</div>
      </>}
      {tab === 'assignments' && <div className="training-table-wrap"><table className="training-table"><thead><tr><th>Course</th><th>Employee</th><th>Progress</th><th>Due date</th><th>Status</th></tr></thead><tbody>{assignments.map((row) => <tr key={row.id}><td><strong>{row.course_title}</strong></td><td>{row.employee_name}</td><td><div className="training-mini-progress"><span style={{ width: `${row.progress_percentage}%` }}/></div><small>{row.progress_percentage}%</small></td><td>{formatDate(row.due_date)}</td><td><span className={`training-status ${row.status}`}>{row.status.replace('_', ' ')}</span></td></tr>)}</tbody></table>{!assignments.length && <div className="training-empty">No training assignments yet.</div>}</div>}
      {tab === 'certificates' && <div className="training-certificate-grid">{certificates.map((item) => <article key={item.id}><Award size={25}/><div><strong>{item.course_title}</strong><small>{item.certificate_code}</small><small>Issued {formatDate(item.issued_at)}</small></div></article>)}{!certificates.length && <div className="training-empty">Certificates earned after completing all lessons will appear here.</div>}</div>}
    </>}

    {showCreate && <div className="training-backdrop"><form className="training-modal" onSubmit={createCourse}><header><div><span className="training-eyebrow">COURSE BUILDER</span><h2>Create a learning course</h2></div><button type="button" onClick={() => setShowCreate(false)}><X size={18}/></button></header><div className="training-form-grid"><label className="full">Course title<input required minLength="3" value={courseForm.title} onChange={(e) => updateField('title', e.target.value)} placeholder="e.g. Information security essentials"/></label><label className="full">Description<textarea value={courseForm.description} onChange={(e) => updateField('description', e.target.value)} rows="3" placeholder="What will employees learn?"/></label><label>Category<input value={courseForm.category} onChange={(e) => updateField('category', e.target.value)}/></label><label>Level<select value={courseForm.level} onChange={(e) => updateField('level', e.target.value)}><option value="beginner">Beginner</option><option value="intermediate">Intermediate</option><option value="advanced">Advanced</option></select></label><label>Duration (minutes)<input type="number" min="1" value={courseForm.duration_minutes} onChange={(e) => updateField('duration_minutes', e.target.value)}/></label><label className="training-check"><input type="checkbox" checked={courseForm.is_mandatory} onChange={(e) => updateField('is_mandatory', e.target.checked)}/> Mandatory training</label></div><div className="training-lesson-builder"><div><strong>Course lessons</strong><button type="button" onClick={() => setCourseForm((current) => ({ ...current, lessons: [...current.lessons, { title: '', description: '', content: '', duration_minutes: 10, order_index: current.lessons.length, is_preview: false }] }))}><Plus size={13}/> Add lesson</button></div>{courseForm.lessons.map((lesson, index) => <section key={index}><label>Lesson {index + 1}<input required minLength="2" value={lesson.title} onChange={(e) => updateLesson(index, 'title', e.target.value)} placeholder="Lesson title"/></label><label>Learning content<textarea value={lesson.content} onChange={(e) => updateLesson(index, 'content', e.target.value)} rows="2" placeholder="Add instructions, notes or lesson text"/></label><div className="training-lesson-options"><label>Minutes<input type="number" min="1" value={lesson.duration_minutes} onChange={(e) => updateLesson(index, 'duration_minutes', e.target.value)}/></label><label className="training-check"><input type="checkbox" checked={lesson.is_preview} onChange={(e) => updateLesson(index, 'is_preview', e.target.checked)}/> Preview lesson</label>{courseForm.lessons.length > 1 && <button type="button" onClick={() => setCourseForm((current) => ({ ...current, lessons: current.lessons.filter((_, i) => i !== index) }))}>Remove</button>}</div></section>)}</div><footer><label className="training-check"><input type="checkbox" checked={courseForm.published} onChange={(e) => updateField('published', e.target.checked)}/> Publish immediately</label><button type="button" className="training-outline" onClick={() => setShowCreate(false)}>Cancel</button><button className="training-primary" disabled={saving}>{saving ? 'Saving…' : 'Create course'}</button></footer></form></div>}

    {selectedCourse && <div className="training-backdrop"><section className="training-modal training-assign-modal"><header><div><span className="training-eyebrow">LEARNER ASSIGNMENT</span><h2>Assign {selectedCourse.title}</h2></div><button onClick={() => setSelectedCourse(null)}><X size={18}/></button></header><label className="training-assign-search">Select employees <select multiple value={selectedEmployees} onChange={(e) => setSelectedEmployees(Array.from(e.target.selectedOptions, (option) => option.value))}>{employees.map((person) => <option key={person.id} value={person.id}>{person.full_name || person.name || person.email}</option>)}</select><small>Use Ctrl (Windows) or Command (Mac) to select multiple employees.</small></label><label className="training-due">Due date<input type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)}/></label><footer><button className="training-outline" onClick={() => setSelectedCourse(null)}>Cancel</button><button className="training-primary" disabled={saving || !selectedEmployees.length} onClick={assignCourse}>{saving ? 'Assigning…' : `Assign to ${selectedEmployees.length} employee(s)`}</button></footer></section></div>}

    {selectedAssignment && <div className="training-backdrop"><section className="training-modal training-learning-modal"><header><div><span className="training-eyebrow">YOUR LEARNING PATH</span><h2>{selectedAssignment.course_title}</h2><p>{selectedAssignment.progress_percentage}% completed</p></div><button onClick={() => setSelectedAssignment(null)}><X size={18}/></button></header><div className="training-learning-progress"><span style={{ width: `${selectedAssignment.progress_percentage}%` }}/></div><div className="training-learning-lessons">{selectedAssignment.lessons?.map((lesson, index) => <article key={lesson.id}><span className={lesson.completed ? 'done' : ''}>{lesson.completed ? <CheckCircle2 size={17}/> : index + 1}</span><div><strong>{lesson.title}</strong><small>{lesson.duration_minutes} min {lesson.description ? `· ${lesson.description}` : ''}</small>{lesson.content && <p>{lesson.content}</p>}{lesson.resource_url && <a href={lesson.resource_url} target="_blank" rel="noreferrer">Open learning resource</a>}</div><button className={lesson.completed ? 'completed' : ''} onClick={() => markLesson(lesson)}>{lesson.completed ? 'Completed' : 'Mark complete'}</button></article>)}</div>{selectedAssignment.certificate_code && <div className="training-notice"><Award size={17}/> Certificate issued: {selectedAssignment.certificate_code}</div>}</section></div>}
  </section>;
}
