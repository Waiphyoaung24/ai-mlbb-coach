import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';
import { login, register } from '../lib/auth';

export default function Login() {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      if (isRegister) {
        await register(email, username, password, i18n.language);
      } else {
        await login(email, password);
      }
      navigate('/');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'An error occurred');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6">{t('app_name')}</h1>

        <div className="flex justify-end mb-4">
          <select
            value={i18n.language}
            onChange={(e) => { i18n.changeLanguage(e.target.value); localStorage.setItem('lang', e.target.value); }}
            className="text-sm border rounded px-2 py-1"
          >
            <option value="my">Myanmar</option>
            <option value="en">English</option>
          </select>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input type="email" placeholder={t('email')} value={email} onChange={e => setEmail(e.target.value)}
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          {isRegister && (
            <input type="text" placeholder={t('username')} value={username} onChange={e => setUsername(e.target.value)}
              className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          )}
          <input type="password" placeholder={t('password')} value={password} onChange={e => setPassword(e.target.value)}
            className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500" required />
          {error && <p className="text-red-500 text-sm">{error}</p>}
          <button type="submit"
            className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg py-3 font-semibold hover:opacity-90">
            {isRegister ? t('register') : t('login')}
          </button>
        </form>

        <p className="text-center mt-4 text-sm text-gray-600 cursor-pointer" onClick={() => setIsRegister(!isRegister)}>
          {isRegister ? t('have_account') : t('no_account')}
        </p>
      </div>
    </div>
  );
}
