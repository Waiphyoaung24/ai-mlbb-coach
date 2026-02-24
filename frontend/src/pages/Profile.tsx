import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import api from '../lib/api';

interface UserProfile {
  id: string;
  email: string;
  username: string;
  tier: string;
  mlbb_game_id: string | null;
  mlbb_server_id: string | null;
  mlbb_username: string | null;
  language: string | null;
}

interface ValidationResult {
  valid: boolean;
  game_id: string;
  server_id: string;
  username: string | null;
  country: string | null;
  error: string | null;
}

export default function Profile() {
  const { t } = useTranslation();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [gameId, setGameId] = useState('');
  const [serverId, setServerId] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [linking, setLinking] = useState(false);
  const [validation, setValidation] = useState<ValidationResult | null>(null);

  useEffect(() => {
    api.get('/auth/me').then(res => {
      setProfile(res.data);
      if (res.data.mlbb_game_id) setGameId(res.data.mlbb_game_id);
      if (res.data.mlbb_server_id) setServerId(res.data.mlbb_server_id);
    }).catch(() => {
      setError('Failed to load profile');
    }).finally(() => setLoading(false));
  }, []);

  const handleValidate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    setValidation(null);
    setValidating(true);
    try {
      const res = await api.post('/players/validate-account', {
        game_id: gameId,
        server_id: serverId,
      });
      const data: ValidationResult = res.data;
      if (data.valid) {
        setValidation(data);
      } else {
        setError(data.error || 'Invalid Game ID or Server ID');
      }
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Validation failed');
    } finally {
      setValidating(false);
    }
  };

  const handleConfirmLink = async () => {
    if (!validation?.username) return;
    setError('');
    setMessage('');
    setLinking(true);
    try {
      await api.post('/players/link-account', {
        game_id: validation.game_id,
        server_id: validation.server_id,
        username: validation.username,
      });
      setMessage('Account linked successfully!');
      setValidation(null);
      const res = await api.get('/auth/me');
      setProfile(res.data);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail || 'Failed to link account');
    } finally {
      setLinking(false);
    }
  };

  const handleCancelValidation = () => {
    setValidation(null);
    setError('');
    setMessage('');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <p className="text-gray-400">{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-6 py-4 flex justify-between items-center">
        <Link to="/" className="text-xl font-bold">{t('app_name')}</Link>
      </nav>

      <div className="max-w-2xl mx-auto p-6 mt-8 space-y-6">
        {/* User Info */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold text-indigo-600 mb-4">{t('profile')}</h2>
          <div className="space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">{t('email')}</span>
              <span className="font-medium">{profile?.email}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">{t('username')}</span>
              <span className="font-medium">{profile?.username}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Tier</span>
              <span className="font-medium uppercase">{profile?.tier}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">{t('language')}</span>
              <span className="font-medium">{profile?.language === 'my' ? 'Myanmar' : 'English'}</span>
            </div>
          </div>
        </div>

        {/* MLBB Account Linking */}
        <div className="bg-white rounded-xl shadow-md p-6">
          <h2 className="text-lg font-semibold text-indigo-600 mb-4">{t('link_account')}</h2>

          {profile?.mlbb_game_id ? (
            <div className="space-y-3 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-500">{t('game_id')}</span>
                <span className="font-medium">{profile.mlbb_game_id}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-500">{t('server_id')}</span>
                <span className="font-medium">{profile.mlbb_server_id}</span>
              </div>
              {profile.mlbb_username && (
                <div className="flex justify-between">
                  <span className="text-gray-500">In-Game Name</span>
                  <span className="font-medium">{profile.mlbb_username}</span>
                </div>
              )}
              <p className="text-green-600 text-xs mt-2">MLBB account linked</p>
            </div>
          ) : validation ? (
            /* Step 2: Confirm username */
            <div className="space-y-4">
              <div className="bg-indigo-50 rounded-lg p-4 text-sm">
                <p className="text-gray-700 mb-3">Is this your account?</p>
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-500">In-Game Name</span>
                    <span className="font-bold text-indigo-700">{validation.username}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">{t('game_id')}</span>
                    <span className="font-medium">{validation.game_id}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">{t('server_id')}</span>
                    <span className="font-medium">{validation.server_id}</span>
                  </div>
                  {validation.country && (
                    <div className="flex justify-between">
                      <span className="text-gray-500">Country</span>
                      <span className="font-medium">{validation.country}</span>
                    </div>
                  )}
                </div>
              </div>
              {error && <p className="text-red-500 text-sm">{error}</p>}
              {message && <p className="text-green-600 text-sm">{message}</p>}
              <div className="flex gap-3">
                <button
                  onClick={handleConfirmLink}
                  disabled={linking}
                  className="flex-1 bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg py-3 font-semibold hover:opacity-90 disabled:opacity-50"
                >
                  {linking ? 'Linking...' : 'Confirm & Link'}
                </button>
                <button
                  onClick={handleCancelValidation}
                  className="flex-1 border border-gray-300 text-gray-600 rounded-lg py-3 font-semibold hover:bg-gray-50"
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            /* Step 1: Enter Game ID + Server ID */
            <form onSubmit={handleValidate} className="space-y-4">
              <input
                type="text" placeholder={t('game_id')} value={gameId}
                onChange={e => setGameId(e.target.value)}
                className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              <input
                type="text" placeholder={t('server_id')} value={serverId}
                onChange={e => setServerId(e.target.value)}
                className="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                required
              />
              {error && <p className="text-red-500 text-sm">{error}</p>}
              {message && <p className="text-green-600 text-sm">{message}</p>}
              <button
                type="submit"
                disabled={validating}
                className="w-full bg-gradient-to-r from-indigo-500 to-purple-600 text-white rounded-lg py-3 font-semibold hover:opacity-90 disabled:opacity-50"
              >
                {validating ? 'Validating...' : 'Validate Account'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
