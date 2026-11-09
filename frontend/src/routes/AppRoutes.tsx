import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { AlunoDetail, EmpresaDetail } from '../pages/Details';
import { AlunoForm } from '../pages/AlunoForm';
import { AlunoList } from '../pages/AlunoList';
import { Catalogo } from '../pages/Catalogo';
import { Dashboard } from '../pages/Dashboard';
import { EmpresaForm } from '../pages/EmpresaForm';
import { EmpresaList } from '../pages/EmpresaList';
import { ProfessorDetail } from '../pages/ProfessorDetail';
import { ProfessorForm } from '../pages/ProfessorForm';
import { ProfessorList } from '../pages/ProfessorList';
import { VantagemForm } from '../pages/VantagemForm';
import { VantagemList } from '../pages/VantagemList';

export function AppRoutes() {
  return <BrowserRouter><Routes><Route element={<Layout />}>
    <Route index element={<Dashboard />} />
    <Route path="alunos" element={<AlunoList />} />
    <Route path="alunos/novo" element={<AlunoForm />} />
    <Route path="alunos/:id" element={<AlunoDetail />} />
    <Route path="alunos/:id/editar" element={<AlunoForm />} />
    <Route path="empresas" element={<EmpresaList />} />
    <Route path="empresas/nova" element={<EmpresaForm />} />
    <Route path="empresas/:id" element={<EmpresaDetail />} />
    <Route path="empresas/:id/editar" element={<EmpresaForm />} />
    <Route path="professores" element={<ProfessorList />} />
    <Route path="professores/novo" element={<ProfessorForm />} />
    <Route path="professores/:id" element={<ProfessorDetail />} />
    <Route path="professores/:id/editar" element={<ProfessorForm />} />
    <Route path="vantagens" element={<VantagemList />} />
    <Route path="vantagens/nova" element={<VantagemForm />} />
    <Route path="vantagens/:id/editar" element={<VantagemForm />} />
    <Route path="catalogo" element={<Catalogo />} />
  </Route></Routes></BrowserRouter>;
}
