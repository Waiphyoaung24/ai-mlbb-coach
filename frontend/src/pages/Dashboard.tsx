import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import { logout } from '../lib/auth';

export default function Dashboard() {
  const { t, i18n } = useTranslation();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
        <h1 className="text-xl font-bold">{t('app_name')}</h1>
        <div className="flex items-center gap-4">
          <select value={i18n.language} onChange={e => { i18n.changeLanguage(e.target.value); localStorage.setItem('lang', e.target.value); }}
            className="bg-white/20 border border-white/30 rounded px-2 py-1 text-sm">
            <option value="my">Myanmar</option>
            <option value="en">English</option>
          </select>
          <button onClick={logout} className="text-sm hover:underline">{t('logout')}</button>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <Link to="/chat" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
          <h2 className="text-lg font-semibold text-indigo-600">{t('chat')}</h2>
          <p className="text-gray-500 mt-2">{t('ask_anything')}</p>
        </Link>
        <Link to="/profile" className="bg-white rounded-xl shadow-md p-6 hover:shadow-lg transition">
          <h2 className="text-lg font-semibold text-indigo-600">{t('profile')}</h2>
          <p className="text-gray-500 mt-2">{t('link_account')}</p>
        </Link>
      </div>
    </div>
  );
}
