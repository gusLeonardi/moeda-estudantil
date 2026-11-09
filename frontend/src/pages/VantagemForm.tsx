import { zodResolver } from '@hookform/resolvers/zod';
import { Save } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';
import { PageHeader } from '../components/UI';
import { apiMessage } from '../services/api';
import { empresaService } from '../services/empresaService';
import { vantagemService } from '../services/vantagemService';
import type { Empresa } from '../types';

const schema = z.object({ empresa_id: z.coerce.number().positive('Selecione a empresa'), nome: z.string().min(2), descricao: z.string().min(3), custo: z.coerce.number().int().positive(), imagem_url: z.string().max(500).optional().nullable(), ativa: z.boolean() });
type Form = z.infer<typeof schema>;
export function VantagemForm() {
  const { id } = useParams(); const editing = !!id; const navigate = useNavigate(); const [empresas, setEmpresas] = useState<Empresa[]>([]); const [serverError, setServerError] = useState('');
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<Form>({ resolver: zodResolver(schema), defaultValues: { empresa_id: 0, nome: '', descricao: '', custo: 1, imagem_url: '', ativa: true } });
  useEffect(() => { empresaService.listar().then(setEmpresas).catch(err => setServerError(apiMessage(err))); if (editing) vantagemService.obter(Number(id)).then(item => reset({ empresa_id: item.empresa_id, nome: item.nome, descricao: item.descricao, custo: Number(item.custo), imagem_url: item.imagem_url, ativa: item.ativa })).catch(err => setServerError(apiMessage(err))); }, [id]);
  const submit = async (values: Form) => { try { if (editing) { const { empresa_id: _, ...data } = values; await vantagemService.atualizar(Number(id), data); } else await vantagemService.criar(values); navigate('/vantagens'); } catch (err) { setServerError(apiMessage(err)); } };
  return <><PageHeader eyebrow="Gestão de empresas" title={editing ? 'Editar vantagem' : 'Nova vantagem'} description="Use uma URL local ou estável para a imagem; nenhum upload externo é necessário." /><form onSubmit={handleSubmit(submit)} className="card p-6">{serverError && <p className="mb-4 rounded-xl bg-rose-50 p-3 text-rose-700">{serverError}</p>}<div className="grid gap-5 md:grid-cols-2"><label><span className="label">Empresa</span><select className="field" disabled={editing} {...register('empresa_id')}><option value={0}>Selecione</option>{empresas.map(item => <option key={item.id} value={item.id}>{item.nome}</option>)}</select>{errors.empresa_id && <p className="error">{errors.empresa_id.message}</p>}</label><label><span className="label">Nome</span><input className="field" {...register('nome')} /></label><label className="md:col-span-2"><span className="label">Descrição</span><textarea className="field min-h-28" {...register('descricao')} /></label><label><span className="label">Custo em moedas</span><input type="number" min={1} step={1} className="field" {...register('custo')} /></label><label><span className="label">URL ou caminho da imagem</span><input className="field" placeholder="/images/vantagem.png" {...register('imagem_url')} /></label><label className="flex items-center gap-2"><input type="checkbox" {...register('ativa')} />Vantagem ativa</label></div><div className="mt-6 flex justify-end gap-3"><Link className="btn-secondary" to="/vantagens">Cancelar</Link><button className="btn-primary" disabled={isSubmitting}><Save size={17} />{isSubmitting ? 'Salvando...' : 'Salvar vantagem'}</button></div></form></>;
}
