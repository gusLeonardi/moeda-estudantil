export type Session = { access_token: string; id: number; nome: string; tipo: 'ALUNO'|'PROFESSOR'|'EMPRESA' };
const KEY = 'conquista.session';
export function readSession(): Session | null { try { return JSON.parse(localStorage.getItem(KEY) || 'null'); } catch { return null; } }
export function saveSession(session: Session) { localStorage.setItem(KEY, JSON.stringify(session)); window.dispatchEvent(new Event('conquista-session')); }
export function clearSession() { localStorage.removeItem(KEY); window.dispatchEvent(new Event('conquista-session')); }
