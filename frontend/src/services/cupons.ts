import { api } from './api';

export interface CupomConferencia {
  id: number;
  codigo_cupom: string;
  empresa_id: number;
  aluno_id: number;
  vantagem_id: number;
  vantagem_nome: string;
  custo: number;
  criado_em: string;
  utilizado_em: string | null;
  utilizado: boolean;
}

export interface CupomValidacao extends CupomConferencia {
  mensagem: string;
}

export interface CupomConsultaPayload {
  empresa_id: number;
  codigo_cupom: string;
}

export async function consultarCupom(
  payload: CupomConsultaPayload,
): Promise<CupomConferencia> {
  const response = await api.post<CupomConferencia>(
    '/cupons/consultar',
    payload,
  );

  return response.data;
}

export async function validarCupom(
  payload: CupomConsultaPayload,
): Promise<CupomValidacao> {
  const response = await api.post<CupomValidacao>(
    '/cupons/validar',
    payload,
  );

  return response.data;
}