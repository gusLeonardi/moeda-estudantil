import { Navigate, Outlet } from 'react-router-dom';
import type { ReactNode } from 'react';
import { readSession } from './session';
export function ProtectedRoute({ roles, children }: { roles?: string[]; children?: ReactNode }) {
  const session = readSession();
  if (!session) return <Navigate to="/login" replace />;
  if (roles && !roles.includes(session.tipo)) return <Navigate to="/" replace />;
  return children ?? <Outlet />;
}
