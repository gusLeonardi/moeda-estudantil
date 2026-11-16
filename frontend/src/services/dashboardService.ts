import { api } from './api';
export type DashboardIndicators = { total_alunos: number };
export const dashboardService = { obterIndicadores: async () => (await api.get<DashboardIndicators>('/dashboard/indicadores')).data };
