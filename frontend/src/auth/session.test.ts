import { beforeEach, describe, expect, it } from 'vitest';
import { clearSession, readSession, saveSession, type Session } from './session';

const value: Session = { access_token: 'test-jwt', id: 7, nome: 'Aluno Teste', tipo: 'ALUNO' };

describe('session storage', () => {
  beforeEach(() => { sessionStorage.clear(); localStorage.clear(); });

  it('stores the JWT only in sessionStorage and can read it back', () => {
    saveSession(value);
    expect(JSON.parse(sessionStorage.getItem('conquista.session') || 'null')).toEqual(value);
    expect(localStorage.getItem('conquista.session')).toBeNull();
    expect(readSession()).toEqual(value);
  });

  it('does not restore a persistent legacy localStorage session', () => {
    localStorage.setItem('conquista.session', JSON.stringify(value));
    expect(readSession()).toBeNull();
  });

  it('removes the in-tab session on logout', () => {
    saveSession(value); clearSession();
    expect(readSession()).toBeNull();
  });

  it('accepts an authenticated administrative session', () => {
    const admin: Session = { access_token: 'admin-jwt', id: 0, nome: 'admin', tipo: 'ADMIN' };
    saveSession(admin);
    expect(readSession()).toEqual(admin);
  });
});
