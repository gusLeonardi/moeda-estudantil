import { BrowserRouter, Route, Routes } from 'react-router-dom';

import { Layout } from '../components/Layout';
import { AlunoDetail, EmpresaDetail } from '../pages/Details';
import { AlunoForm } from '../pages/AlunoForm';
import { AlunoList } from '../pages/AlunoList';
import { Catalogo } from '../pages/Catalogo';
import { ConferenciaCupons } from '../pages/ConferenciaCupons';
import { Dashboard } from '../pages/Dashboard';
import { EmpresaForm } from '../pages/EmpresaForm';
import { EmpresaList } from '../pages/EmpresaList';
import { ProfessorDetail } from '../pages/ProfessorDetail';
import { ProfessorForm } from '../pages/ProfessorForm';
import { ProfessorList } from '../pages/ProfessorList';
import { VantagemForm } from '../pages/VantagemForm';
import { VantagemList } from '../pages/VantagemList';
import { Login } from '../pages/Login';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { RegistrationChoice } from '../pages/RegistrationChoice';

export function AppRoutes() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="login" element={<Login />} />
        <Route path="cadastro" element={<RegistrationChoice />} />
        <Route path="cadastro/aluno" element={<AlunoForm />} />
        <Route path="cadastro/professor" element={<ProfessorForm />} />
        <Route path="cadastro/empresa" element={<EmpresaForm />} />
        <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route index element={<Dashboard />} />

          <Route path="alunos" element={<ProtectedRoute roles={['ALUNO','PROFESSOR']}><AlunoList /></ProtectedRoute>} />
          <Route path="alunos/novo" element={<ProtectedRoute roles={['ALUNO']}><AlunoForm /></ProtectedRoute>} />
          <Route path="alunos/:id" element={<ProtectedRoute roles={['ALUNO']}><AlunoDetail /></ProtectedRoute>} />
          <Route path="alunos/:id/editar" element={<ProtectedRoute roles={['ALUNO']}><AlunoForm /></ProtectedRoute>} />

          <Route path="empresas" element={<ProtectedRoute roles={['EMPRESA']}><EmpresaList /></ProtectedRoute>} />
          <Route path="empresas/nova" element={<ProtectedRoute roles={['EMPRESA']}><EmpresaForm /></ProtectedRoute>} />
          <Route path="empresas/:id" element={<ProtectedRoute roles={['EMPRESA']}><EmpresaDetail /></ProtectedRoute>} />
          <Route path="empresas/:id/editar" element={<ProtectedRoute roles={['EMPRESA']}><EmpresaForm /></ProtectedRoute>} />

          <Route path="professores" element={<ProtectedRoute roles={['PROFESSOR']}><ProfessorList /></ProtectedRoute>} />
          <Route path="professores/:id" element={<ProtectedRoute roles={['PROFESSOR']}><ProfessorDetail /></ProtectedRoute>} />
          <Route path="professores/:id/editar" element={<ProtectedRoute roles={['PROFESSOR']}><ProfessorForm /></ProtectedRoute>} />

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
