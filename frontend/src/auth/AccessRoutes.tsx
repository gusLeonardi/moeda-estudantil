import type { ReactNode } from 'react';
import { Navigate, useParams } from 'react-router-dom';
import { readSession } from './session';

export function PublicOnlyRoute({ children }: { children: ReactNode }) {
  return readSession() ? <Navigate to="/" replace /> : children;
}

export function OwnRecordRoute({ role, children }: { role: 'ALUNO' | 'PROFESSOR' | 'EMPRESA'; children: ReactNode }) {
  const { id } = useParams();
  const session = readSession();
  if (!session || session.tipo !== role) return <Navigate to="/" replace />;
  if (String(session.id) !== id) {
    const collection = role === 'ALUNO' ? 'alunos' : role === 'EMPRESA' ? 'empresas' : 'professores';
    return <Navigate to={`/${collection}/${session.id}`} replace />;
  }
  return children;
}

export function StudentAreaHome({ directory }: { directory: ReactNode }) {
  const session = readSession();
  if (session?.tipo === 'ALUNO') return <Navigate to={`/alunos/${session.id}`} replace />;
  if (session?.tipo === 'PROFESSOR') return directory;
  return <Navigate to="/" replace />;
}

export function CompanyProfileHome() {
  const session = readSession();
  return session?.tipo === 'EMPRESA'
    ? <Navigate to={`/empresas/${session.id}`} replace />
    : <Navigate to="/" replace />;
}

export function TeacherProfileHome() {
  const session = readSession();
  return session?.tipo === 'PROFESSOR'
    ? <Navigate to={`/professores/${session.id}`} replace />
    : <Navigate to="/" replace />;
}
