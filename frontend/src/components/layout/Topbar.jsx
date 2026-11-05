import { useLocation } from 'react-router-dom';
import { Bell, Search } from 'lucide-react';
import '../../styles/layout.css';

const pageTitles = {
  '/dashboard': 'Dashboard',
  '/employees': 'Employees',
  '/onboarding': 'Onboarding',
  '/documents': 'Documents',
  '/training': 'Training',
  '/calendar': 'Calendar',
  '/notifications': 'Notifications',
  '/reports': 'Reports',
  '/organization': 'Organization',
  '/settings': 'Settings',
};

export default function Topbar() {
  const { pathname } = useLocation();
  const title = pageTitles[pathname] || 'OnboardX';

  return (
    <header className="topbar">
      <div className="topbar-title">{title}</div>
      <div className="topbar-actions">
        <button className="topbar-icon-btn" title="Search">
          <Search size={17} />
        </button>
        <button className="topbar-icon-btn" title="Notifications">
          <Bell size={17} />
          <span className="notification-dot" />
        </button>
      </div>
    </header>
  );
}
