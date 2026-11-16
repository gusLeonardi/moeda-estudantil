import { zodResolver } from '@hookform/resolvers/zod';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { AddressFields, TextField, addressDefaults } from '../components/FormFields';
import { PageHeader, State } from '../components/UI';
import { adminService } from '../services/adminService';
import { apiMessage } from '../services/api';
import { instituicaoService } from '../services/instituicaoService';
import type { AdminProfessor, Instituicao } from '../types';
import { isValidCpf, onlyDigits } from '../utils/validation';

const addressSchema = z.object({
  logradouro: z.string().trim().min(2), numero: z.string().trim().min(1),
  complemento: z.string().optional().nullable(), bairro: z.string().trim().min(2),
  cidade: z.string().trim().min(2), estado: z.string().length(2),
  cep: z.string().regex(/^\D*(?:\d\D*){8}$/),
});
const schema = z.object({
  nome: z.string().trim().min(2).max(150), email: z.string().email().max(254),
  cpf: z.string().refine(isValidCpf, 'Informe um CPF válido.'),
  departamento: z.string().trim().min(2).max(150),
  instituicao_id: z.coerce.number().positive('Selecione uma instituição.'),
  endereco: addressSchema,
});
type FormValues = z.infer<typeof schema>;

export function AdminProfessorManager() {
  const [items, setItems] = useState<AdminProfessor[]>([]);
  const [instituicoes, setInstituicoes] = useState<Instituicao[]>([]);
  const [query, setQuery] = useState('');
  const [selected, setSelected] = useState<AdminProfessor | null>(null);
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const { register, handleSubmit, reset, formState: { errors, isSubmitting } } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { nome: '', email: '', cpf: '', departamento: '', instituicao_id: 0, endereco: addressDefaults },
  });

  const load = async (search = query) => {
    setLoading(true);
    try { setItems(await adminService.listarProfessores(search)); setError(''); }
    catch (cause) { setError(apiMessage(cause)); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    instituicaoService.listar().then(setInstituicoes).catch(cause => setError(apiMessage(cause)));
  }, []);
  useEffect(() => {
    const timer = window.setTimeout(() => { void load(query); }, 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  const startCreate = () => {
    setSelected(null); setEditing(false); setNotice('');
    reset({ nome: '', email: '', cpf: '', departamento: '', instituicao_id: 0, endereco: addressDefaults });
  };
  const startEdit = (person: AdminProfessor) => {
    setSelected(person); setEditing(true); setNotice('');
    reset({ nome: person.nome, email: person.email, cpf: person.cpf, departamento: person.departamento, instituicao_id: person.instituicao.id, endereco: { ...person.endereco, cep: person.endereco.cep } });
  };
  const inspect = async (person: AdminProfessor) => {
    try { setSelected(await adminService.obterProfessor(person.id)); setEditing(false); setNotice(''); }
    catch (cause) { setError(apiMessage(cause)); }
  };

  const submit = async (values: FormValues) => {
    setError(''); setNotice('');
    const clean = { ...values, cpf: onlyDigits(values.cpf), endereco: { ...values.endereco, cep: onlyDigits(values.endereco.cep) } };
    try {
      if (editing && selected) {
        const { cpf: _cpf, ...data } = clean;
        const updated = await adminService.atualizarProfessor(selected.id, data);
        setSelected(updated); setNotice('Cadastro atualizado.');
      } else {
        const result = await adminService.criarProfessor(clean);
        setSelected(result.professor);
        setEditing(false);
        setNotice(result.activation_sent
          ? 'Professor pré-cadastrado. O convite de ativação foi enviado por e-mail.'
          : 'Professor pré-cadastrado, mas o e-mail não foi entregue. Verifique o SMTP e reenvie o convite.');
      }
      await load();
    } catch (cause) { setError(apiMessage(cause)); }
  };

  const resend = async (person: AdminProfessor) => {
    setError(''); setNotice('');
    try {
      const result = await adminService.reenviarAtivacao(person.id);
      setNotice(result.delivered ? 'Novo convite enviado.' : result.detail || 'Não foi possível entregar o convite. Verifique o SMTP.');
      await load();
    } catch (cause) { setError(apiMessage(cause)); }
  };

  return <>
    <PageHeader eyebrow="Administração institucional" title="Professores" description="Pré-cadastre, consulte e atualize professores. O saldo inicial de 1.000 moedas é atribuído pelo sistema." action={<button className="btn-primary" type="button" onClick={startCreate}>Novo professor</button>} />
    {(error || notice) && <p role={error ? 'alert' : 'status'} className={`mb-4 rounded-xl p-3 text-sm ${error ? 'bg-rose-50 text-rose-700' : 'bg-emerald-50 text-emerald-800'}`}>{error || notice}</p>}
    <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,.8fr)]">
      <section className="card overflow-hidden">
        <div className="border-b border-slate-100 p-4"><label className="block"><span className="sr-only">Buscar professor</span><input className="field" value={query} onChange={event => setQuery(event.target.value)} placeholder="Buscar por nome, e-mail, CPF ou departamento" /></label></div>
        <State loading={loading} error="" empty={!items.length}>
          {!!items.length && <div className="overflow-x-auto"><table className="w-full min-w-[650px] text-left"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="px-4 py-3">Professor</th><th>Departamento</th><th>Instituição</th><th>Conta</th><th className="px-4">Ações</th></tr></thead><tbody className="divide-y divide-slate-100">{items.map(person => <tr key={person.id}><td className="px-4 py-3"><b className="block">{person.nome}</b><small className="text-slate-500">{person.email}</small></td><td>{person.departamento}</td><td>{person.instituicao.sigla}</td><td><span className={person.conta_ativada ? 'text-emerald-700' : 'text-amber-700'}>{person.conta_ativada ? 'Ativada' : 'Pendente'}</span></td><td className="px-4"><div className="flex gap-2"><button className="btn-secondary !px-3 !py-2" onClick={() => void inspect(person)}>Consultar</button><button className="btn-secondary !px-3 !py-2" onClick={() => startEdit(person)}>Editar</button>{!person.conta_ativada && <button className="btn-secondary !px-3 !py-2" onClick={() => void resend(person)}>Reenviar convite</button>}</div></td></tr>)}</tbody></table></div>}
        </State>
      </section>

      <section className="card p-5 sm:p-6">
        <h2 className="mb-4 text-xl font-bold">{editing ? 'Editar professor' : selected ? 'Dados do professor' : 'Pré-cadastrar professor'}</h2>
        {!editing && selected ? <div className="space-y-2 text-sm"><p><b>Nome:</b> {selected.nome}</p><p><b>CPF:</b> {selected.cpf}</p><p><b>E-mail:</b> {selected.email}</p><p><b>Departamento:</b> {selected.departamento}</p><p><b>Instituição:</b> {selected.instituicao.nome}</p><p><b>Saldo:</b> {Number(selected.saldo).toFixed(2)} moedas</p><p><b>Ativação:</b> {selected.conta_ativada ? 'Concluída' : 'Aguardando o professor definir a senha pelo convite'}</p><p><b>Endereço:</b> {selected.endereco.logradouro}, {selected.endereco.numero} — {selected.endereco.bairro}, {selected.endereco.cidade}/{selected.endereco.estado}, {selected.endereco.cep}</p><button className="btn-secondary mt-3" onClick={() => startEdit(selected)}>Editar cadastro</button></div> : <form className="space-y-4" onSubmit={handleSubmit(submit)}>
          <TextField label="Nome completo" name="nome" register={register} error={errors.nome?.message} />
          <TextField label="E-mail institucional" name="email" type="email" register={register} error={errors.email?.message} />
          <TextField label="CPF" name="cpf" register={register} mask="cpf" placeholder="000.000.000-00" disabled={editing} error={errors.cpf?.message} />
          <TextField label="Departamento" name="departamento" register={register} error={errors.departamento?.message} />
          <label className="block"><span className="label">Instituição de ensino</span><select className="field" {...register('instituicao_id')}><option value={0}>Selecione</option>{instituicoes.map(institution => <option key={institution.id} value={institution.id}>{institution.sigla} — {institution.nome}</option>)}</select>{errors.instituicao_id && <small className="text-rose-700">{errors.instituicao_id.message}</small>}</label>
          <AddressFields register={register} errors={errors} />
          {!editing && <p className="rounded-lg bg-teal-50 p-3 text-sm text-teal-900">A senha será criada pelo próprio professor após receber o convite de ativação.</p>}
          <div className="flex gap-2"><button className="btn-primary" disabled={isSubmitting}>{isSubmitting ? 'Salvando…' : editing ? 'Salvar alterações' : 'Cadastrar e enviar convite'}</button>{(editing || selected) && <button className="btn-secondary" type="button" onClick={startCreate}>Novo cadastro</button>}</div>
        </form>}
      </section>
    </div>
  </>;
}
