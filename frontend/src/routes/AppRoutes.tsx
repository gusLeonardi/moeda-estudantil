import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Layout } from '../components/Layout';
import { AlunoDetail, EmpresaDetail } from '../pages/Details';
import { AlunoForm } from '../pages/AlunoForm';
import { AlunoList } from '../pages/AlunoList';
import { Catalogo } from '../pages/Catalogo';
import { ConferenciaCupons } from '../pages/ConferenciaCupons';
import { Dashboard } from '../pages/Dashboard';
import { EmpresaForm } from '../pages/EmpresaForm';
import { ProfessorDetail } from '../pages/ProfessorDetail';
import { ProfessorForm } from '../pages/ProfessorForm';
import { VantagemForm } from '../pages/VantagemForm';
import { VantagemList } from '../pages/VantagemList';
import { Login } from '../pages/Login';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { RegistrationChoice } from '../pages/RegistrationChoice';
import { AdminLogin } from '../pages/AdminLogin';
import { AdminProfessorManager } from '../pages/AdminProfessorManager';
import { CompanyProfileHome, OwnRecordRoute, PublicOnlyRoute, StudentAreaHome, TeacherProfileHome } from '../auth/AccessRoutes';
import { Navigate } from 'react-router-dom';

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="login" element={<Login />} />
        <Route path="admin/login" element={<AdminLogin />} />
        <Route path="cadastro" element={<PublicOnlyRoute><RegistrationChoice /></PublicOnlyRoute>} />
        <Route path="cadastro/aluno" element={<PublicOnlyRoute><AlunoForm /></PublicOnlyRoute>} />
        <Route path="cadastro/empresa" element={<PublicOnlyRoute><EmpresaForm /></PublicOnlyRoute>} />
        <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="admin/professores" element={<ProtectedRoute roles={['ADMIN']}><AdminProfessorManager /></ProtectedRoute>} />

          <Route path="alunos" element={<ProtectedRoute roles={['ALUNO','PROFESSOR']}><StudentAreaHome directory={<AlunoList />} /></ProtectedRoute>} />
          <Route path="alunos/novo" element={<Navigate to="/cadastro/aluno" replace />} />
          <Route path="alunos/:id" element={<ProtectedRoute roles={['ALUNO']}><OwnRecordRoute role="ALUNO"><AlunoDetail /></OwnRecordRoute></ProtectedRoute>} />
          <Route path="alunos/:id/editar" element={<ProtectedRoute roles={['ALUNO']}><OwnRecordRoute role="ALUNO"><AlunoForm /></OwnRecordRoute></ProtectedRoute>} />

          <Route path="empresas" element={<ProtectedRoute roles={['EMPRESA']}><CompanyProfileHome /></ProtectedRoute>} />
          <Route path="empresas/nova" element={<Navigate to="/cadastro/empresa" replace />} />
          <Route path="empresas/:id" element={<ProtectedRoute roles={['EMPRESA']}><OwnRecordRoute role="EMPRESA"><EmpresaDetail /></OwnRecordRoute></ProtectedRoute>} />
          <Route path="empresas/:id/editar" element={<ProtectedRoute roles={['EMPRESA']}><OwnRecordRoute role="EMPRESA"><EmpresaForm /></OwnRecordRoute></ProtectedRoute>} />

          <Route path="professores" element={<ProtectedRoute roles={['PROFESSOR']}><TeacherProfileHome /></ProtectedRoute>} />
          <Route path="professores/:id" element={<ProtectedRoute roles={['PROFESSOR']}><OwnRecordRoute role="PROFESSOR"><ProfessorDetail /></OwnRecordRoute></ProtectedRoute>} />
          <Route path="professores/:id/editar" element={<ProtectedRoute roles={['PROFESSOR']}><OwnRecordRoute role="PROFESSOR"><ProfessorForm /></OwnRecordRoute></ProtectedRoute>} />

          <Route path="vantagens" element={<ProtectedRoute roles={['EMPRESA']}><VantagemList /></ProtectedRoute>} />
          <Route path="vantagens/nova" element={<ProtectedRoute roles={['EMPRESA']}><VantagemForm /></ProtectedRoute>} />
          <Route path="vantagens/:id/editar" element={<ProtectedRoute roles={['EMPRESA']}><VantagemForm /></ProtectedRoute>} />

          <Route path="catalogo" element={<ProtectedRoute roles={['ALUNO']}><Catalogo /></ProtectedRoute>} />
          <Route path="cupons" element={<ProtectedRoute roles={['EMPRESA']}><ConferenciaCupons /></ProtectedRoute>} />
        </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
