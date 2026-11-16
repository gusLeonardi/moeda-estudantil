import { Navigate } from 'react-router-dom';
import { readSession } from '../auth/session';

/** Legacy route component: a company session can open only its own profile. */
export function EmpresaList() {
  const session = readSession();
  return session?.tipo === 'EMPRESA'
    ? <Navigate to={`/empresas/${session.id}`} replace />
    : <Navigate to="/" replace />;
}
