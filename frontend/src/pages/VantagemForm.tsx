import { zodResolver } from '@hookform/resolvers/zod';
import { ImagePlus, Save } from 'lucide-react';
import { useEffect, useState } from 'react';
import { useForm } from 'react-hook-form';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { z } from 'zod';
import { PageHeader } from '../components/UI';
import { apiMessage } from '../services/api';
import { vantagemService } from '../services/vantagemService';

const secureImageUrl = z.string().trim().url('Informe uma URL válida').refine(value => {
  try { return new URL(value).protocol === 'https:'; } catch { return false; }
}, 'A imagem deve usar HTTPS.');
const schema = z.object({ nome: z.string().trim().min(2, 'Informe um nome'), descricao: z.string().trim().min(3, 'Descreva a vantagem'), custo: z.coerce.number().int().positive('O custo deve ser maior que zero'), imagem_url: secureImageUrl, ativa: z.boolean() });
type Form = z.infer<typeof schema>;

export function VantagemForm() {
  const { id } = useParams(); const editing = !!id; const navigate = useNavigate();
  const [serverError, setServerError] = useState('');
  const { register, handleSubmit, reset, watch, formState: { errors, isSubmitting } } = useForm<Form>({ resolver: zodResolver(schema), defaultValues: { nome: '', descricao: '', custo: 1, imagem_url: '', ativa: true } });
  const imageUrl = watch('imagem_url');

  useEffect(() => {
    if (editing) vantagemService.obter(Number(id)).then(item => reset({ nome: item.nome, descricao: item.descricao, custo: Number(item.custo), imagem_url: item.imagem_url ?? '', ativa: item.ativa })).catch(err => setServerError(apiMessage(err)));
  }, [id, editing, reset]);

  const submit = async (values: Form) => {
    setServerError('');
    try {
      if (editing) await vantagemService.atualizar(Number(id), values);
      else await vantagemService.criar(values);
      navigate('/vantagens');
    } catch (err) { setServerError(apiMessage(err)); }
  };

  return <div className="mx-auto max-w-4xl">
    <PageHeader eyebrow="Vantagens da comunidade" title={editing ? 'Editar vantagem' : 'Cadastrar vantagem'} description="Informe os detalhes do benefício e adicione uma imagem disponível em uma URL HTTPS pública." />
    <form onSubmit={handleSubmit(submit)} className="card p-5 sm:p-8">
      {serverError && <p role="alert" className="mb-5 rounded-xl border border-rose-200 bg-rose-50 p-3 text-sm text-rose-700">{serverError}</p>}
      <div className="grid gap-5 sm:grid-cols-2">
        <label><span className="label">Nome da vantagem</span><input className="field" placeholder="Ex.: Desconto no almoço" {...register('nome')} />{errors.nome && <p className="error">{errors.nome.message}</p>}</label>
        <label className="sm:col-span-2"><span className="label">Descrição</span><textarea className="field min-h-28" placeholder="Explique o benefício, as condições e como resgatar." {...register('descricao')} />{errors.descricao && <p className="error">{errors.descricao.message}</p>}</label>
        <label><span className="label">Custo em moedas</span><input type="number" min={1} step={1} className="field" {...register('custo')} />{errors.custo && <p className="error">{errors.custo.message}</p>}</label>
        <label><span className="label">Imagem do produto ou benefício</span><input type="url" required className="field" placeholder="https://exemplo.com/imagem.jpg" autoComplete="url" {...register('imagem_url')} />{errors.imagem_url && <p className="error">{errors.imagem_url.message}</p>}<span className="mt-1 block text-xs text-slate-500">A URL precisa ser pública e usar HTTPS. Hospede a imagem em armazenamento permanente.</span></label>
        {imageUrl && <div className="sm:col-span-2"><span className="label">Prévia da imagem</span><div className="flex min-h-40 items-center justify-center overflow-hidden rounded-2xl border border-dashed border-slate-300 bg-slate-50">{secureImageUrl.safeParse(imageUrl).success ? <img className="max-h-64 w-full object-contain" src={imageUrl} alt="Prévia da vantagem" onError={event => { event.currentTarget.hidden = true; }} /> : <div className="flex items-center gap-2 p-5 text-sm text-slate-400"><ImagePlus size={20} /> A prévia aparecerá após inserir uma URL HTTPS válida</div>}</div></div>}
        <label className="flex items-center gap-2 text-sm font-semibold text-slate-700"><input type="checkbox" className="h-4 w-4 accent-blue-700" {...register('ativa')} />Vantagem ativa</label>
      </div>
      <div className="mt-8 flex flex-col-reverse justify-end gap-3 border-t border-slate-100 pt-5 sm:flex-row"><Link className="btn-secondary" to="/vantagens">Cancelar</Link><button className="btn-primary" disabled={isSubmitting}><Save size={17} />{isSubmitting ? 'Salvando...' : editing ? 'Salvar alterações' : 'Cadastrar vantagem'}</button></div>
    </form>
  </div>;
}
