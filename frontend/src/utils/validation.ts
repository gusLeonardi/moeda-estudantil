export const onlyDigits = (value: string) => value.replace(/\D/g, '');

function hasValidCheckDigits(value: string, baseLength: number, weights: number[][]) {
  const digits = onlyDigits(value);
  if (digits.length !== baseLength + 2 || new Set(digits).size === 1) return false;
  const numbers = [...digits].map(Number);
  return weights.every((currentWeights, index) => {
    const remainder = currentWeights.reduce((sum, weight, position) => sum + numbers[position] * weight, 0) % 11;
    const expected = remainder < 2 ? 0 : 11 - remainder;
    return numbers[baseLength + index] === expected;
  });
}

export const isValidCpf = (value: string) => hasValidCheckDigits(value, 9, [[10, 9, 8, 7, 6, 5, 4, 3, 2], [11, 10, 9, 8, 7, 6, 5, 4, 3, 2]]);
export const isValidCnpj = (value: string) => hasValidCheckDigits(value, 12, [[5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2], [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]]);
export const formatCpf = (value: string) => onlyDigits(value).replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
export const formatCnpj = (value: string) => onlyDigits(value).replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})/, '$1.$2.$3/$4-$5');
export const formatCep = (value: string) => onlyDigits(value).replace(/(\d{5})(\d{3})/, '$1-$2');
