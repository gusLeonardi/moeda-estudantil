import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it } from 'vitest';
import { MemoryRouter, Route, Routes, useParams } from 'react-router-dom';
import { OwnRecordRoute, PublicOnlyRoute, StudentAreaHome } from './AccessRoutes';
import { clearSession, saveSession, type Session } from './session';

const student: Session = { access_token: 'jwt-student', id: 7, nome: 'Aluna', tipo: 'ALUNO' };
function ProfileMarker() { const { id } = useParams(); return <span>Perfil {id}</span>; }

function renderAt(path: string) {
  return render(<MemoryRouter initialEntries={[path]}><Routes>
    <Route path="/cadastro/aluno" element={<PublicOnlyRoute><span>Formulário público</span></PublicOnlyRoute>} />
    <Route path="/alunos" element={<StudentAreaHome directory={<span>Diretório docente</span>} />} />
    <Route path="/alunos/:id" element={<OwnRecordRoute role="ALUNO"><ProfileMarker /></OwnRecordRoute>} />
    <Route path="/" element={<span>Início</span>} />
  </Routes></MemoryRouter>);
}

describe('rotas de cadastro e perfil de aluno', () => {
  beforeEach(() => { sessionStorage.clear(); localStorage.clear(); });
  afterEach(() => { cleanup(); clearSession(); });

  it('permite que visitante abra diretamente o formulário público', () => {
    renderAt('/cadastro/aluno');
    expect(screen.getByText('Formulário público')).toBeInTheDocument();
  });

  it('redireciona aluno autenticado para fora do cadastro público', () => {
    saveSession(student);
    renderAt('/cadastro/aluno');
    expect(screen.getByText('Início')).toBeInTheDocument();
    expect(screen.queryByText('Formulário público')).not.toBeInTheDocument();
  });

  it('mostra o próprio perfil ao abrir a área do aluno', () => {
    saveSession(student);
    renderAt('/alunos');
    expect(screen.getByText('Perfil 7')).toBeInTheDocument();
    expect(screen.queryByText('Diretório docente')).not.toBeInTheDocument();
  });

  it('redireciona acesso direto ao perfil de outro aluno para o próprio perfil', () => {
    saveSession(student);
    renderAt('/alunos/99');
    expect(screen.getByText('Perfil 7')).toBeInTheDocument();
  });
});
