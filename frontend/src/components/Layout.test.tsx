import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { Layout } from './Layout';
import { clearSession, saveSession, type Session } from '../auth/session';

const sessions: Session[] = [
  { access_token: 'student', id: 1, nome: 'Aluna', tipo: 'ALUNO' },
  { access_token: 'teacher', id: 2, nome: 'Professor', tipo: 'PROFESSOR' },
  { access_token: 'company', id: 3, nome: 'Empresa', tipo: 'EMPRESA' },
  { access_token: 'admin', id: 0, nome: 'Admin', tipo: 'ADMIN' },
];

function renderLayout(session: Session) {
  saveSession(session);
  return render(<MemoryRouter><Layout /></MemoryRouter>);
}

describe('menu por perfil', () => {
  beforeEach(() => { sessionStorage.clear(); localStorage.clear(); });
  afterEach(() => { cleanup(); clearSession(); });

  it('aluno vê apenas o próprio perfil e o catálogo, sem cadastro ou diretório', () => {
    renderLayout(sessions[0]);
    expect(screen.getByRole('link', { name: 'Meu perfil' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Catálogo e resgates/ })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Alunos' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Novo aluno/ })).not.toBeInTheDocument();
  });

  it('empresa vê o próprio perfil e os fluxos empresariais sem catálogo do aluno', () => {
    renderLayout(sessions[2]);
    expect(screen.getByRole('link', { name: 'Meu perfil' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Gerenciar vantagens' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Conferência de cupons/ })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Catálogo e resgates/ })).not.toBeInTheDocument();
  });

  it('professor tem diretório de leitura e perfil, sem ações de cadastro', () => {
    renderLayout(sessions[1]);
    expect(screen.getByRole('link', { name: 'Alunos' })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Meu perfil' })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Novo aluno/ })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: /Gestão de professores/ })).not.toBeInTheDocument();
  });

  it('admin vê apenas gerenciamento institucional de professores', () => {
    renderLayout(sessions[3]);
    expect(screen.getByRole('link', { name: /Gestão de professores/ })).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Alunos' })).not.toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Empresas' })).not.toBeInTheDocument();
  });
});
