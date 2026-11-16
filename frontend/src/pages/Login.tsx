import { useState, type FormEvent } from 'react';
import { ArrowLeft, ArrowRight, GraduationCap, KeyRound, LockKeyhole, Mail, ShieldCheck } from 'lucide-react';
import { Link, useLocation, useNavigate } from 'react-router-dom';

import { saveSession, type Session } from '../auth/session';
import { api, apiMessage } from '../services/api';

type Mode = 'login' | 'request' | 'complete';

export function Login() {
  const [mode, setMode] = useState<Mode>('login');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [token, setToken] = useState('');
  const [erro, setErro] = useState('');
  const location = useLocation();
  const [notice, setNotice] = useState(() => (location.state as { success?: string } | null)?.success ?? '');
  const navigate = useNavigate();

  async function submit(event: FormEvent) {
    event.preventDefault(); setErro(''); setNotice('');
    try {
      if (mode === 'login') {
        const { data } = await api.post<Session>('/auth/login', { email, senha });
        saveSession(data); navigate('/', { replace: true }); return;
      }
      if (mode === 'request') {
        await api.post('/auth/activation/request', { email }); setMode('complete');
        setNotice('Se a conta puder ser ativada, enviaremos um token ao e-mail cadastrado. Confira também a pasta de spam.'); return;
      }
      await api.post('/auth/activation/complete', { email, token: token.trim(), senha });
      setMode('login'); setToken(''); setSenha(''); setNotice('Senha definida. Entre usando seu e-mail e a nova senha.');
    } catch (error) { setErro(apiMessage(error)); }
  }

  const isLogin = mode === 'login';
  const heading = isLogin ? 'Boas-vindas de volta' : mode === 'request' ? 'Vamos ativar sua conta' : 'Defina sua senha';
  const subtitle = isLogin ? 'Entre para acompanhar suas moedas e vantagens.' : mode === 'request' ? 'Informe o e-mail já associado à sua conta. Enviaremos um token para esse endereço.' : 'Use o token enviado ao seu e-mail e escolha uma senha segura.';

  return <main className="min-h-[calc(100vh-2rem)] bg-slate-50 px-4 py-8 sm:grid sm:place-items-center sm:py-12">
    <div className="mx-auto grid w-full max-w-5xl overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-xl shadow-slate-200/60 lg:grid-cols-[.9fr_1.1fr]">
      <aside className="relative hidden overflow-hidden bg-gradient-to-br from-blue-950 via-blue-900 to-teal-800 p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute -right-24 -top-24 h-72 w-72 rounded-full border-[40px] border-white/5" />
        <div className="relative">
          <Link to="/" className="inline-flex items-center gap-3"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-teal-300 text-blue-950"><GraduationCap size={27} /></span><span><b className="block text-xl">Conquista</b><small className="text-blue-100">Moeda Estudantil</small></span></Link>
          <div className="mt-20 max-w-sm"><p className="text-sm font-bold uppercase tracking-[.18em] text-teal-200">Sua jornada começa aqui</p><h1 className="mt-4 text-4xl font-extrabold leading-tight">Reconheça conquistas. Aproveite vantagens.</h1><p className="mt-5 leading-7 text-blue-100">Um espaço para conectar alunos, professores e empresas parceiras.</p></div>
        </div>
        <div className="relative flex items-center gap-3 rounded-2xl border border-white/10 bg-white/10 p-4 text-sm text-blue-50"><ShieldCheck className="shrink-0 text-teal-200" size={22} /> Acesso protegido para cada perfil da comunidade.</div>
      </aside>

      <section className="p-6 sm:p-10 lg:p-14">
        <Link to="/" className="inline-flex items-center gap-2 text-sm font-bold text-blue-900 lg:hidden"><GraduationCap size={22} /> Conquista</Link>
        <div className="mt-8 lg:mt-4">
          <div className="mb-6 grid h-12 w-12 place-items-center rounded-2xl bg-blue-50 text-blue-800"><LockKeyhole size={23} /></div>
          <p className="text-sm font-bold uppercase tracking-[.16em] text-teal-700">Portal Conquista</p>
          <h2 className="mt-2 text-3xl font-extrabold tracking-tight text-slate-950">{heading}</h2>
          <p className="mt-2 max-w-md text-sm leading-6 text-slate-500">{subtitle}</p>
        </div>

        <form className="mt-8 grid gap-5" onSubmit={submit}>
          <label className="block"><span className="label">E-mail</span><span className="relative block"><Mail className="pointer-events-none absolute left-3.5 top-3 text-slate-400" size={18} /><input className="field pl-11" type="email" autoComplete="email" placeholder="voce@exemplo.com" required value={email} onChange={event => setEmail(event.target.value)} /></span></label>
          {isLogin && <label className="block"><span className="label">Senha</span><span className="relative block"><KeyRound className="pointer-events-none absolute left-3.5 top-3 text-slate-400" size={18} /><input className="field pl-11" type="password" autoComplete="current-password" placeholder="Sua senha" required value={senha} onChange={event => setSenha(event.target.value)} /></span></label>}
          {mode === 'complete' && <>
            <label className="block"><span className="label">Token de ativação</span><input className="field font-mono tracking-wide" autoComplete="one-time-code" placeholder="Cole aqui o token do e-mail" required value={token} onChange={event => setToken(event.target.value.trim())} /></label>
            <label className="block"><span className="label">Crie uma senha</span><input className="field" type="password" autoComplete="new-password" minLength={12} placeholder="Pelo menos 12 caracteres" required value={senha} onChange={event => setSenha(event.target.value)} /><span className="mt-1.5 block text-xs text-slate-500">Use no mínimo 12 caracteres.</span></label>
          </>}
          {erro && <p role="alert" className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{erro}</p>}
          {notice && <p role="status" className="rounded-xl border border-teal-200 bg-teal-50 px-4 py-3 text-sm text-teal-800">{notice}</p>}
          <button className="btn-primary mt-1 min-h-12 justify-center" type="submit" disabled={false}>{isLogin ? <>Entrar na minha conta <ArrowRight size={17} /></> : mode === 'request' ? 'Enviar token de ativação' : 'Ativar conta e definir senha'}</button>
        </form>

        <div className="mt-6 flex flex-col gap-3 border-t border-slate-100 pt-5 text-sm">
          {isLogin && <><Link className="font-semibold text-blue-800 hover:text-blue-950" to="/cadastro">Ainda não tem conta? <span className="underline underline-offset-4">Cadastre-se</span></Link><button className="w-fit text-left text-slate-500 hover:text-slate-800" type="button" onClick={() => { setMode('request'); setErro(''); setNotice(''); }}>Ativar uma conta antiga</button></>}
          {mode === 'complete' && <button className="w-fit text-left text-slate-500 hover:text-slate-800" type="button" onClick={() => { setMode('request'); setToken(''); setErro(''); setNotice(''); }}>Solicitar outro token</button>}
          {!isLogin && <button className="inline-flex w-fit items-center gap-2 text-slate-500 hover:text-slate-800" type="button" onClick={() => { setMode('login'); setErro(''); setNotice(''); }}><ArrowLeft size={16} /> Voltar ao login</button>}
        </div>
      </section>
    </div>
  </main>;
}
