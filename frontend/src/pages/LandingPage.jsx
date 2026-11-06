import { Link } from 'react-router-dom';
import {
  ArrowRight, ArrowUpRight, BadgeCheck, BarChart3, Building2, CalendarCheck2,
  Check, ChevronRight, ClipboardCheck, FileCheck2, Layers3, LockKeyhole,
  Menu, ShieldCheck, Sparkles, Users, Workflow, X,
} from 'lucide-react';
import { useState } from 'react';
import '../styles/landing.css';

const capabilities = [
  { icon: Users, title: 'People directory', description: 'Keep employee records, teams, departments and reporting lines organized in one reliable workspace.' },
  { icon: Workflow, title: 'Guided onboarding', description: 'Turn repeatable onboarding plans into clear stages, assigned tasks and visible progress.' },
  { icon: FileCheck2, title: 'Document control', description: 'Collect employee documents, follow review decisions and keep important records together.' },
  { icon: BarChart3, title: 'Operational visibility', description: 'Give HR teams a quick view of workforce activity, onboarding progress and pending work.' },
  { icon: CalendarCheck2, title: 'Coordinated work', description: 'Bring important employee activities and upcoming milestones into a shared workflow.' },
  { icon: ShieldCheck, title: 'Role-aware access', description: 'Separate HR administration and employee self-service with role-based permissions.' },
];

const steps = [
  { number: '01', title: 'Set up your workspace', description: 'Create your organization and invite your team with a private organization code.' },
  { number: '02', title: 'Build a repeatable process', description: 'Create onboarding templates, define stages and assign responsibilities.' },
  { number: '03', title: 'Follow progress together', description: 'Employees complete their tasks while HR keeps track of the overall journey.' },
];

export default function LandingPage() {
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return (
    <div className="landing-page">
      <header className="landing-nav">
        <Link className="landing-brand" to="/" onClick={closeMenu} aria-label="OnboardX home">
          <span className="landing-brand-mark"><Layers3 size={19} strokeWidth={2.2} /></span>
          <span>Onboard<span>X</span></span>
        </Link>
        <button className="landing-menu-toggle" type="button" onClick={() => setMenuOpen((open) => !open)} aria-label={menuOpen ? 'Close navigation' : 'Open navigation'}>
          {menuOpen ? <X size={21} /> : <Menu size={21} />}
        </button>
        <nav className={`landing-nav-links${menuOpen ? ' is-open' : ''}`} aria-label="Main navigation">
          <a href="#platform" onClick={closeMenu}>Platform</a>
          <a href="#workflow" onClick={closeMenu}>How it works</a>
          <a href="#security" onClick={closeMenu}>Security</a>
          <Link className="landing-nav-login" to="/login" onClick={closeMenu}>Sign in</Link>
          <Link className="landing-nav-cta" to="/register" onClick={closeMenu}>Get started <ArrowUpRight size={15} /></Link>
        </nav>
      </header>

      <main>
        <section className="landing-hero">
          <div className="landing-hero-copy">
            <div className="landing-eyebrow"><Sparkles size={14} /> PEOPLE OPERATIONS, MADE CLEAR</div>
            <h1>Make every first day feel like a <em>great beginning.</em></h1>
            <p className="landing-hero-description">One thoughtful workspace for employee onboarding, people records and the everyday work that helps teams feel ready from day one.</p>
            <div className="landing-hero-actions">
              <Link className="landing-primary-button" to="/register">Create your workspace <ArrowRight size={17} /></Link>
              <Link className="landing-secondary-button" to="/login">Explore your workspace <ChevronRight size={17} /></Link>
            </div>
            <div className="landing-trust-line"><span><Check size={14} /> Structured onboarding</span><span><Check size={14} /> HR and employee views</span></div>
          </div>

          <div className="landing-preview-wrap" aria-label="OnboardX workspace preview">
            <div className="landing-preview-glow" />
            <div className="landing-preview-card">
              <div className="preview-topbar"><div className="preview-brand"><span className="preview-brand-dot" /> OnboardX <small>/ Overview</small></div><div className="preview-avatar">HR</div></div>
              <div className="preview-welcome"><div><span className="preview-kicker">MONDAY, PEOPLE OVERVIEW</span><h2>Your team, in focus.</h2><p>A clear view of what is moving today.</p></div><span className="preview-date">Workspace</span></div>
              <div className="preview-metrics">
                <div className="preview-metric"><span>Total employees</span><strong>128</strong><small><i className="preview-positive" /> Team directory</small></div>
                <div className="preview-metric"><span>Onboarding</span><strong>12</strong><small>In progress</small></div>
                <div className="preview-metric"><span>To review</span><strong>08</strong><small>Pending actions</small></div>
              </div>
              <div className="preview-lower">
                <div className="preview-panel preview-progress"><div className="preview-panel-heading">Onboarding progress <span>View all</span></div><div className="preview-progress-row"><div><b>Engineering</b><small>New team members</small></div><strong>76%</strong></div><div className="preview-track"><span style={{ width: '76%' }} /></div><div className="preview-progress-row"><div><b>People & Culture</b><small>New team members</small></div><strong>92%</strong></div><div className="preview-track"><span style={{ width: '92%' }} /></div><div className="preview-progress-row"><div><b>Operations</b><small>New team members</small></div><strong>58%</strong></div><div className="preview-track"><span style={{ width: '58%' }} /></div></div>
                <div className="preview-panel preview-tasks"><div className="preview-panel-heading">Today’s focus <span>03 items</span></div><div className="preview-task"><span className="preview-task-icon coral"><FileCheck2 size={14} /></span><div><b>Review documents</b><small>Priya Sharma</small></div><span className="preview-task-status">Review</span></div><div className="preview-task"><span className="preview-task-icon green"><ClipboardCheck size={14} /></span><div><b>Complete orientation</b><small>Arjun Rao</small></div><span className="preview-task-status done">Ready</span></div><div className="preview-task"><span className="preview-task-icon sand"><Users size={14} /></span><div><b>Assign a buddy</b><small>New joiner · Today</small></div><span className="preview-task-status">Open</span></div></div>
              </div>
            </div>
            <div className="landing-float-note"><span><BadgeCheck size={17} /></span><div><b>Every step has a place</b><small>One connected employee journey</small></div></div>
          </div>
        </section>

        <section className="landing-proof-strip" aria-label="Platform principles">
          <span>BUILT FOR PEOPLE TEAMS</span><b><Building2 size={17} /> Organization-ready</b><b><LockKeyhole size={17} /> Role-aware access</b><b><ClipboardCheck size={17} /> Repeatable workflows</b>
        </section>

        <section className="landing-section" id="platform">
          <div className="landing-section-heading"><div className="landing-eyebrow">A CONNECTED PEOPLE WORKSPACE</div><h2>Less chasing. More <em>meaningful progress.</em></h2><p>Bring the moving parts of employee onboarding into a shared, organized experience for HR teams and employees.</p></div>
          <div className="landing-feature-grid">{capabilities.map(({ icon: Icon, title, description }, index) => <article className="landing-feature-card" key={title}><div className={`landing-feature-icon tone-${index + 1}`}><Icon size={20} /></div><h3>{title}</h3><p>{description}</p><span className="landing-feature-number">0{index + 1}</span></article>)}</div>
        </section>

        <section className="landing-workflow-section" id="workflow">
          <div className="landing-workflow-intro"><div className="landing-eyebrow">A SIMPLE WAY FORWARD</div><h2>From welcome to <em>work-ready.</em></h2><p>Give every new joiner a consistent experience, while keeping the people team informed at each step.</p><Link to="/register" className="landing-text-link">Start with your organization <ArrowUpRight size={16} /></Link></div>
          <div className="landing-steps">{steps.map((step) => <article className="landing-step" key={step.number}><span>{step.number}</span><div><h3>{step.title}</h3><p>{step.description}</p></div></article>)}</div>
        </section>

        <section className="landing-security" id="security"><div className="landing-security-icon"><ShieldCheck size={24} /></div><div><div className="landing-eyebrow">BUILT WITH RESPONSIBILITY IN MIND</div><h2>Right information. <em>Right access.</em></h2><p>OnboardX separates HR administration from employee self-service and scopes workspace data by organization, helping teams manage employee information with care.</p></div><Link to="/register" aria-label="Create an OnboardX workspace"><ArrowUpRight size={22} /></Link></section>

        <section className="landing-cta"><div className="landing-eyebrow">MAKE THE NEXT FIRST DAY COUNT</div><h2>Give your people a better <em>start.</em></h2><p>Bring your onboarding process and employee workspace together with OnboardX.</p><Link to="/register" className="landing-primary-button">Create your workspace <ArrowRight size={17} /></Link></section>
      </main>

      <footer className="landing-footer"><Link className="landing-brand" to="/"><span className="landing-brand-mark"><Layers3 size={18} /></span><span>Onboard<span>X</span></span></Link><span>People operations, thoughtfully organized.</span><div><Link to="/login">Sign in</Link><Link to="/register">Get started</Link></div><small>© {new Date().getFullYear()} OnboardX</small></footer>
    </div>
  );
}
