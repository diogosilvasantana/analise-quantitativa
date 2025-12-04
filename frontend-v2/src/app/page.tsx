import { Dashboard } from '@/components/dashboard/Dashboard';

export const metadata = {
  title: 'AI-TRADER-PRO Dashboard',
};

export default function Home() {
  return (
    <main className="min-h-screen">
      <Dashboard />
    </main>
  );
}
