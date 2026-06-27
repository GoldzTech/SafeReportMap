import { useEffect, useState } from 'react';
import { ArrowLeft, Lock, LogIn, ShieldAlert } from 'lucide-react';
import SafeReportAdminDashboard from './dashboard';
import PublicReportForm from './pages/public_report_form';
import {
  clearStoredAuthSession,
  getStoredAuthSession,
  loginAdmin,
  setStoredAuthSession,
} from './lib/api';

const DEFAULT_ADMIN_EMAIL = import.meta.env.VITE_DEMO_ADMIN_EMAIL || 'admin@safereport.com';

function normalizePath(pathname) {
  if (!pathname || pathname === '/') return '/';
  return pathname.replace(/\/+$/, '') || '/';
}

function navigate(path, replace = false) {
  if (replace) {
    window.history.replaceState({}, '', path);
  } else {
    window.history.pushState({}, '', path);
  }
  window.dispatchEvent(new PopStateEvent('popstate'));
}

function AdminLogin({ onSuccess, onCancel }) {
  const [email, setEmail] = useState(DEFAULT_ADMIN_EMAIL);
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');

    try {
      const session = await loginAdmin({
        email: email.trim(),
        password,
      });

      setStoredAuthSession(session);
      onSuccess(session);
    } catch (err) {
      setError(err?.message || 'Não foi possível autenticar.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 text-slate-100">
      <div className="w-full max-w-md rounded-3xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl">
        <div className="mb-6 flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-violet-500 text-slate-950">
            <ShieldAlert className="h-5 w-5" />
          </div>
          <div>
            <div className="text-sm font-semibold text-white">SafeReport Map</div>
            <div className="text-xs text-slate-400">Acesso restrito</div>
          </div>
        </div>

        <h1 className="text-2xl font-semibold text-white">Entrada administrativa</h1>
        <p className="mt-2 text-sm leading-6 text-slate-400">
          Entre com as credenciais do administrador para acessar a área interna.
        </p>

        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
              <ShieldAlert className="h-3.5 w-3.5" />
              E-mail
            </div>
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
              placeholder="admin@safereport.com"
              type="email"
              autoComplete="email"
            />
          </div>

          <div className="rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3">
            <div className="mb-2 flex items-center gap-2 text-xs uppercase tracking-wide text-slate-500">
              <Lock className="h-3.5 w-3.5" />
              Senha
            </div>
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-transparent text-sm text-white outline-none placeholder:text-slate-600"
              placeholder="Sua senha"
              type="password"
              autoComplete="current-password"
            />
          </div>

          {error ? (
            <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={loading}
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
          >
            <LogIn className="h-4 w-4" />
            {loading ? 'Entrando...' : 'Entrar'}
          </button>

          <button
            type="button"
            onClick={onCancel}
            className="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-medium text-white transition hover:bg-white/10"
          >
            <ArrowLeft className="h-4 w-4" />
            Voltar ao relato
          </button>
        </form>
      </div>
    </div>
  );
}

export default function App() {
  const [pathname, setPathname] = useState(normalizePath(window.location.pathname));
  const [authSession, setAuthSession] = useState(() => getStoredAuthSession());

  useEffect(() => {
    const onPopState = () => setPathname(normalizePath(window.location.pathname));
    window.addEventListener('popstate', onPopState);
    return () => window.removeEventListener('popstate', onPopState);
  }, []);

  useEffect(() => {
    if (pathname === '/admin/login' && authSession) {
      navigate('/admin', true);
      return;
    }

    if (pathname.startsWith('/admin') && !authSession && pathname !== '/admin/login') {
      navigate('/admin/login', true);
    }
  }, [pathname, authSession]);

  const handleLoginSuccess = (session) => {
    setAuthSession(session);
    navigate('/admin', true);
  };

  const handleLogout = () => {
    clearStoredAuthSession();
    setAuthSession(null);
    navigate('/admin/login', true);
  };

  if (pathname.startsWith('/admin')) {
    if (!authSession) {
      return (
        <AdminLogin
          onSuccess={handleLoginSuccess}
          onCancel={() => navigate('/', true)}
        />
      );
    }

    return <SafeReportAdminDashboard onLogout={handleLogout} />;
  }

  return <PublicReportForm />;
}