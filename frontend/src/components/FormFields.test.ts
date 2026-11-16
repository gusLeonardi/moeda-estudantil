import { describe, expect, it } from 'vitest';
import { maskValue } from './FormFields';

describe('registration input masks', () => {
  it('formats CPF, CNPJ and CEP', () => {
    expect(maskValue('52998224725', 'cpf')).toBe('529.982.247-25');
    expect(maskValue('11222333000181', 'cnpj')).toBe('11.222.333/0001-81');
    expect(maskValue('30535901', 'cep')).toBe('30535-901');
  });

  it('formats landline and mobile telephone lengths correctly', () => {
    expect(maskValue('3133334444', 'telefone')).toBe('(31) 3333-4444');
    expect(maskValue('31999994444', 'telefone')).toBe('(31) 99999-4444');
  });
});
