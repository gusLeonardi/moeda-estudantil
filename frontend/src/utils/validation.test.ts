import { describe, expect, it } from 'vitest';
import { formatCnpj, formatCpf, isValidCnpj, isValidCpf } from './validation';

describe('validação de documentos', () => {
  it('aceita CPF com dígitos verificadores válidos e rejeita inválidos', () => {
    expect(isValidCpf('529.982.247-25')).toBe(true);
    expect(isValidCpf('123.456.789-01')).toBe(false);
    expect(isValidCpf('111.111.111-11')).toBe(false);
  });

  it('aceita CNPJ com dígitos verificadores válidos e rejeita inválidos', () => {
    expect(isValidCnpj('11.222.333/0001-81')).toBe(true);
    expect(isValidCnpj('12.345.678/0001-99')).toBe(false);
    expect(isValidCnpj('11.111.111/1111-11')).toBe(false);
  });

  it('formata documentos para exibição', () => {
    expect(formatCpf('52998224725')).toBe('529.982.247-25');
    expect(formatCnpj('11222333000181')).toBe('11.222.333/0001-81');
  });
});
