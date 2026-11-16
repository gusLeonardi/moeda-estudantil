import { api } from './api';
import type { Session } from '../auth/session';
import type { AdminProfessor, AdminProfessorCreate, AdminProfessorCreated, ProfessorUpdate } from '../types';

export const adminService = {
  login: async (username: string, senha: string) =>
    (await api.post<Session>('/admin/auth/login', { username, senha })).data,
  listarProfessores: async (busca = '') =>
    (await api.get<AdminProfessor[]>('/admin/professores', { params: { busca: busca || undefined } })).data,
  obterProfessor: async (id: number) =>
    (await api.get<AdminProfessor>(`/admin/professores/${id}`)).data,
  criarProfessor: async (data: AdminProfessorCreate) =>
    (await api.post<AdminProfessorCreated>('/admin/professores', data)).data,
  atualizarProfessor: async (id: number, data: ProfessorUpdate) =>
    (await api.put<AdminProfessor>(`/admin/professores/${id}`, data)).data,
  reenviarAtivacao: async (id: number) =>
    (await api.post<{ accepted: boolean; delivered: boolean; detail?: string }>(`/admin/professores/${id}/ativacao`)).data,
};
