import{api}from'./api';import type{Instituicao}from'../types';export const instituicaoService={listar:async()=>(await api.get<Instituicao[]>('/instituicoes')).data};
