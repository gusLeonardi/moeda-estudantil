import { api } from './api';
import type { Resgate, Vantagem, VantagemCreate, VantagemUpdate } from '../types';

export const vantagemService = {
  listar: async (apenasAtivas = false) => (await api.get<Vantagem[]>('/vantagens', { params: { apenas_ativas: apenasAtivas } })).data,
  catalogo: async () => (await api.get<Vantagem[]>('/vantagens/catalogo')).data,
  minhas: async () => (await api.get<Vantagem[]>('/vantagens/minhas')).data,
  obter: async (id: number) => (await api.get<Vantagem>(`/vantagens/${id}`)).data,
  criar: async (data: VantagemCreate) => (await api.post<Vantagem>('/vantagens', data)).data,
  atualizar: async (id: number, data: VantagemUpdate) => (await api.put<Vantagem>(`/vantagens/${id}`, data)).data,
  desativar: async (id: number) => (await api.post<Vantagem>(`/vantagens/${id}/desativar`)).data,
  ativar: async (id: number) => (await api.post<Vantagem>(`/vantagens/${id}/ativar`)).data,
  excluir: async (id: number) => { await api.delete(`/vantagens/${id}`); },
  resgatar: async (vantagemId: number, idempotencyKey: string) => (await api.post<Resgate>('/resgates', { vantagem_id: vantagemId, idempotency_key: idempotencyKey })).data,
};
