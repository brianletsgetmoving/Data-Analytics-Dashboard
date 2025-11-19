import { BarChart3 } from 'lucide-react';

function Header() {
  return (
    <header className="neo-glass mb-6">
      <div className="flex items-center gap-4">
        <BarChart3 className="w-8 h-8" style={{ color: 'var(--accent-primary)' }} />
        <h1 className="text-2xl font-bold neo-text-primary">
          Data Analytics Dashboard
        </h1>
      </div>
    </header>
  );
}

export default Header;

