import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard, Users, ClipboardList, FileText,
  BookOpen, Bell, Calendar, BarChart2, Settings, Target,
  LogOut, Building2, UserRound
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import '../../styles/sidebar.css';

const navItems = [
  { label: 'Main', items: [
    { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  ]},
  { label: 'People', items: [
    { to: '/employees', icon: Users, label: 'Employees' },
    { to: '/profile', icon: UserRound, label: 'My Profile' },
    { to: '/departments', icon: Building2, label: 'Departments' },
    { to: '/onboarding', icon: ClipboardList, label: 'Onboarding' },
  ]},
  { label: 'Work', items: [
    { to: '/documents', icon: FileText, label: 'Documents' },
    { to: '/training', icon: BookOpen, label: 'Training' },
    { to: '/performance', icon: Target, label: 'Performance' },
    { to: '/calendar', icon: Calendar, label: 'Calendar' },
  ]},
  { label: 'Insights', items: [
    { to: '/notifications', icon: Bell, label: 'Notifications' },
    { to: '/reports', icon: BarChart2, label: 'Reports' },
  ]},
  { label: 'Admin', items: [
    { to: '/organization', icon: Building2, label: 'Organization' },
    { to: '/settings', icon: Settings, label: 'Settings' },
  ]},
];

const roleLabels = {
  SUPER_ADMIN: 'Super Admin',
  HR_ADMIN: 'HR Admin',
  MANAGER: 'Manager',
  EMPLOYEE: 'Employee',
};

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const initials = user?.full_name
    ? user.full_name.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : 'U';

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-text">Onboard<span>X</span></div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map(section => (
          <div key={section.label}>
            <div className="sidebar-section-label">{section.label}</div>
            {section.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}
              >
                <Icon size={16} />
                {label}
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-user">
          <div className="sidebar-avatar">{initials}</div>
          <div className="sidebar-user-info">
            <div className="sidebar-user-name">{user?.full_name || 'User'}</div>
            <div className="sidebar-user-role">{roleLabels[user?.role] || user?.role}</div>
          </div>
          <button className="logout-btn" onClick={handleLogout} title="Logout">
            <LogOut size={15} />
          </button>
        </div>
      </div>
    </aside>
  );
}
