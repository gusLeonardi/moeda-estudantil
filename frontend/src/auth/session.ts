export type Session = { access_token: string; id: number; nome: string; tipo: 'ALUNO'|'PROFESSOR'|'EMPRESA' };
const KEY = 'conquista.session';
try { localStorage.removeItem(KEY); } catch { /* Storage may be disabled by the browser. */ }

export function readSession(): Session | null {
  try {
    const value = JSON.parse(sessionStorage.getItem(KEY) || 'null') as Session | null;
    if (!value || typeof value.access_token !== 'string' || !['ALUNO', 'PROFESSOR', 'EMPRESA'].includes(value.tipo)) return null;
    return value;
  } catch { return null; }
}

export function saveSession(session: Session) {
  sessionStorage.setItem(KEY, JSON.stringify(session));
  window.dispatchEvent(new Event('conquista-session'));
}

export function clearSession() {
  sessionStorage.removeItem(KEY);
  window.dispatchEvent(new Event('conquista-session'));
}
