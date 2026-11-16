import { FormEvent, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { saveSession } from '../auth/session';
import { apiMessage } from '../services/api';
import { adminService } from '../services/adminService';

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [senha, setSenha] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    setError('');
    setBusy(true);
    try {
      const session = await adminService.login(username.trim(), senha);
      if (session.tipo !== 'ADMIN') throw new Error('Perfil administrativo inválido.');
      saveSession(session);
      navigate('/admin/professores', { replace: true });
    } catch (cause) {
      setError(apiMessage(cause));
    } finally {
      setBusy(false);
    }
  };

  return (
    <main className="grid min-h-screen place-items-center bg-slate-50 px-4 py-10">
      <form className="card w-full max-w-md space-y-5 p-7" onSubmit={submit}>
        <div>
          <p className="text-xs font-bold uppercase tracking-widest text-teal-700">Conquista · Administração</p>
          <h1 className="mt-2 text-2xl font-extrabold text-slate-900">Acesso administrativo</h1>
          <p className="mt-2 text-sm text-slate-600">Use as credenciais administrativas provisionadas no servidor.</p>
        </div>
        {error && <p role="alert" className="rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
        <label className="block"><span className="label">Usuário</span><input className="field" autoComplete="username" required maxLength={100} value={username} onChange={event => setUsername(event.target.value)} /></label>
        <label className="block"><span className="label">Senha</span><input className="field" type="password" autoComplete="current-password" required maxLength={128} value={senha} onChange={event => setSenha(event.target.value)} /></label>
        <button className="btn-primary w-full justify-center" disabled={busy}>{busy ? 'Validando…' : 'Entrar na administração'}</button>
        <Link className="block text-center text-sm font-semibold text-teal-800" to="/login">Voltar ao login</Link>
      </form>
    </main>
  );
}
