import { api } from './api';
import type { Resgate, Vantagem, VantagemCreate, VantagemUpdate } from '../types';

export const vantagemService = {
  listar: async (apenasAtivas = false, empresaId?: number) => (await api.get<Vantagem[]>('/vantagens', { params: { apenas_ativas: apenasAtivas, empresa_id: empresaId } })).data,
  obter: async (id: number) => (await api.get<Vantagem>(`/vantagens/${id}`)).data,
  criar: async (data: VantagemCreate) => (await api.post<Vantagem>('/vantagens', data)).data,
  atualizar: async (id: number, data: VantagemUpdate) => (await api.put<Vantagem>(`/vantagens/${id}`, data)).data,
  desativar: async (id: number) => (await api.post<Vantagem>(`/vantagens/${id}/desativar`)).data,
  resgatar: async (alunoId: number, vantagemId: number, idempotencyKey: string) => (await api.post<Resgate>('/resgates', { aluno_id: alunoId, vantagem_id: vantagemId, idempotency_key: idempotencyKey })).data,
};
