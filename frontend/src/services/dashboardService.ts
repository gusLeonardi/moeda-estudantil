import { api } from './api';
export type DashboardIndicators = { total_alunos: number; total_empresas: number; total_professores: number; total_vantagens: number };
export const dashboardService = { obterIndicadores: async () => (await api.get<DashboardIndicators>('/dashboard/indicadores')).data };
