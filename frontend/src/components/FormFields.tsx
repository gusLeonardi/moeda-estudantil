import type { ChangeEvent } from 'react';
import type { FieldErrors, UseFormRegister } from 'react-hook-form';

export const addressDefaults = { logradouro: '', numero: '', complemento: '', bairro: '', cidade: '', estado: 'MG', cep: '' };

export type InputMask = 'cpf' | 'cnpj' | 'cep' | 'telefone';

export function maskValue(value: string, mask?: InputMask) {
  const digits = value.replace(/\D/g, '');
  if (mask === 'cpf') return digits.slice(0, 11).replace(/^(\d{3})(\d)/, '$1.$2').replace(/^(\d{3}\.\d{3})(\d)/, '$1.$2').replace(/^(\d{3}\.\d{3}\.\d{3})(\d)/, '$1-$2');
  if (mask === 'cnpj') return digits.slice(0, 14).replace(/^(\d{2})(\d)/, '$1.$2').replace(/^(\d{2}\.\d{3})(\d)/, '$1.$2').replace(/^(\d{2}\.\d{3}\.\d{3})(\d)/, '$1/$2').replace(/^(\d{2}\.\d{3}\.\d{3}\/\d{4})(\d)/, '$1-$2');
  if (mask === 'cep') return digits.slice(0, 8).replace(/^(\d{5})(\d)/, '$1-$2');
  if (mask === 'telefone') {
    const phone = digits.slice(0, 11);
    if (phone.length <= 2) return phone ? `(${phone}` : '';
    const local = phone.slice(2);
    const prefixLength = phone.length > 10 ? 5 : 4;
    return `(${phone.slice(0, 2)}) ${local.slice(0, prefixLength)}${local.length > prefixLength ? `-${local.slice(prefixLength)}` : ''}`;
  }
  return value;
}

export function TextField({ label, name, register, error, disabled = false, type = 'text', placeholder, mask, autoComplete }: {
  label: string; name: string; register: UseFormRegister<any>; error?: string; disabled?: boolean; type?: string;
  placeholder?: string; mask?: InputMask; autoComplete?: string;
}) {
  const field = register(name);
  return <label className="block">
    <span className="label">{label}</span>
    <input type={type} disabled={disabled} placeholder={placeholder} autoComplete={autoComplete} inputMode={mask ? 'numeric' : undefined}
      className="field disabled:bg-slate-100" {...field}
      onChange={(event: ChangeEvent<HTMLInputElement>) => { event.target.value = maskValue(event.target.value, mask); void field.onChange(event); }} />
    {error && <p className="error">{error}</p>}
  </label>;
}

export function AddressFields({ register, errors }: { register: UseFormRegister<any>; errors: FieldErrors<any> }) {
  const e = (errors.endereco as any) || {};
  return <>
    <div className="col-span-full mt-2 border-t border-slate-100 pt-5"><h3 className="font-bold text-slate-900">Endereço</h3><p className="mt-1 text-sm text-slate-500">Informe onde podemos localizar você ou sua empresa.</p></div>
    <div className="sm:col-span-2"><TextField label="Logradouro" name="endereco.logradouro" register={register} error={e.logradouro?.message} placeholder="Rua, avenida, praça..." /></div>
    <TextField label="Número" name="endereco.numero" register={register} error={e.numero?.message} />
    <TextField label="Complemento" name="endereco.complemento" register={register} placeholder="Apto, sala (opcional)" />
    <TextField label="Bairro" name="endereco.bairro" register={register} error={e.bairro?.message} />
    <TextField label="Cidade" name="endereco.cidade" register={register} error={e.cidade?.message} />
    <TextField label="UF" name="endereco.estado" register={register} error={e.estado?.message} placeholder="MG" />
    <TextField label="CEP" name="endereco.cep" register={register} error={e.cep?.message} mask="cep" placeholder="00000-000" />
  </>;
}
