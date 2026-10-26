import{describe,expect,it}from'vitest';import{apiMessage}from'./api';
describe('apiMessage',()=>{it('fornece mensagem segura para erros desconhecidos',()=>{expect(apiMessage(new Error('segredo interno'))).toBe('Não foi possível concluir a operação.')})});
