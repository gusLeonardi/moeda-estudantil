import { zodResolver } from '@hookform/resolvers/zod';
import { ArrowLeft, Save } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';
import { AddressFields, TextField, addressDefaults } from '../components/FormFields';
import { PageHeader } from '../components/UI';
import { apiMessage } from '../services/api';
import { instituicaoService } from '../services/instituicaoService';
import { professorService } from '../services/professorService';
import type { Instituicao } from '../types';
import { isValidCpf, onlyDigits } from '../utils/validation';

const address = z.object({ logradouro: z.string().min(2), numero: z.string().min(1), complemento: z.string().optional().nullable(), bairro: z.string().min(2), cidade: z.string().min(2), estado: z.string().length(2), cep: z.string().regex(/^\D*(?:\d\D*){8}$/) });
const schema = z.object({ nome: z.string().trim().min(2), email: z.string().email(), cpf: z.string().refine(isValidCpf, 'CPF inválido'), departamento: z.string().trim().min(2), instituicao_id: z.coerce.number().positive(), endereco: address });
type Form = z.infer<typeof schema>;

export function ProfessorForm() {
  const { id } = useParams(); const editing = !!id; const navigate = useNavigate();
  const [instituicoes, setInstituicoes] = useState<Instituicao[]>([]); const [serverError, setServerError] = useState('');
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<Form>({ resolver: zodResolver(schema), defaultValues: { nome: '', email: '', cpf: '', departamento: '', instituicao_id: 0, endereco: addressDefaults } });
  useEffect(() => { instituicaoService.listar().then(setInstituicoes).catch(error => setServerError(apiMessage(error))); if (editing) professorService.obter(Number(id)).then(item => reset({ ...item, instituicao_id: item.instituicao.id })).catch(error => setServerError(apiMessage(error))); }, [id]);
  const submit = async (values: Form) => { setServerError(''); try { const clean = { ...values, cpf: onlyDigits(values.cpf), endereco: { ...values.endereco, cep: onlyDigits(values.endereco.cep) } }; if (editing) { const { cpf: _, ...data } = clean; await professorService.atualizar(Number(id), data); } else await professorService.criar(clean); navigate('/professores'); } catch (error) { setServerError(apiMessage(error)); } };
  return <><PageHeader eyebrow="Administração local" title={editing ? 'Editar professor' : 'Novo professor'} description="O saldo começa em 1.000 moedas e não pode ser editado manualmente." /><form className="card p-5 sm:p-7" onSubmit={handleSubmit(submit)}>{serverError && <p className="mb-5 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}<div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-4"><div className="sm:col-span-2"><TextField label="Nome" name="nome" register={register} error={errors.nome?.message} /></div><TextField label="E-mail" name="email" type="email" register={register} error={errors.email?.message} /><TextField label="CPF" name="cpf" register={register} disabled={editing} error={errors.cpf?.message} /><div className="sm:col-span-2"><TextField label="Departamento" name="departamento" register={register} error={errors.departamento?.message} /></div><label className="sm:col-span-2"><span className="label">Instituição</span><select className="field" {...register('instituicao_id')}><option value={0}>Selecione</option>{instituicoes.map(item => <option key={item.id} value={item.id}>{item.sigla} · {item.nome}</option>)}</select></label><AddressFields register={register} errors={errors} /></div><div className="mt-7 flex justify-end gap-3"><Link className="btn-secondary" to="/professores"><ArrowLeft size={17} />Cancelar</Link><button className="btn-primary" disabled={isSubmitting}><Save size={17} />{isSubmitting ? 'Salvando...' : 'Salvar professor'}</button></div></form></>;
}
