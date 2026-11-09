import { api } from './api';
import type { ExtratoAluno, ExtratoProfessor, Professor, ProfessorCreate, ProfessorUpdate, Transferencia } from '../types';

export const professorService = {
  listar: async (busca = '') => (await api.get<Professor[]>('/professores', { params: { busca: busca || undefined } })).data,
  obter: async (id: number) => (await api.get<Professor>(`/professores/${id}`)).data,
  criar: async (data: ProfessorCreate) => (await api.post<Professor>('/professores', data)).data,
  atualizar: async (id: number, data: ProfessorUpdate) => (await api.put<Professor>(`/professores/${id}`, data)).data,
  excluir: async (id: number) => { await api.delete(`/professores/${id}`); },
  transferir: async (data: { professor_id: number; aluno_id: number; quantidade: number; justificativa: string }) => (await api.post<Transferencia>('/moedas/transferencias', data)).data,
  extrato: async (id: number) => (await api.get<ExtratoProfessor>(`/professores/${id}/extrato`)).data,
  extratoAluno: async (id: number) => (await api.get<ExtratoAluno>(`/alunos/${id}/extrato`)).data,
};
