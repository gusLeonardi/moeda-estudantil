import { Ban, Pencil, Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, State } from '../components/UI';
import { apiMessage } from '../services/api';
import { vantagemService } from '../services/vantagemService';
import type { Vantagem } from '../types';

export function VantagemList() {
  const [items, setItems] = useState<Vantagem[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  const load = () => { setLoading(true); vantagemService.listar().then(setItems).catch(err => setError(apiMessage(err))).finally(() => setLoading(false)); };
  useEffect(load, []);
  const deactivate = async (item: Vantagem) => { if (!window.confirm(`Desativar ${item.nome}?`)) return; try { await vantagemService.desativar(item.id); load(); } catch (err) { setError(apiMessage(err)); } };
  return <><PageHeader eyebrow="Gestão administrativa" title="Vantagens" description="Benefícios oferecidos pelas empresas parceiras." action={<Link className="btn-primary" to="/vantagens/nova"><Plus size={18} />Nova vantagem</Link>} /><div className="mb-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">Sem autenticação: gerenciamento disponível apenas para demonstração local.</div><State loading={loading} error={error} empty={!items.length}><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{items.map(item => <article key={item.id} className="card overflow-hidden">{item.imagem_url ? <img src={item.imagem_url} alt="" className="h-40 w-full bg-slate-100 object-cover" /> : <div className="grid h-40 place-items-center bg-slate-100 text-slate-400">Sem imagem</div>}<div className="p-5"><div className="flex items-start justify-between gap-3"><div><h2 className="font-bold">{item.nome}</h2><p className="text-sm text-slate-500">{item.empresa_nome}</p></div><span className={`rounded-full px-2 py-1 text-xs font-bold ${item.ativa ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{item.ativa ? 'Ativa' : 'Inativa'}</span></div><p className="mt-3 text-sm text-slate-600">{item.descricao}</p><p className="mt-4 text-xl font-extrabold text-teal-700">{Number(item.custo).toFixed(2)} moedas</p><div className="mt-4 flex gap-2"><Link className="btn-secondary" to={`/vantagens/${item.id}/editar`}><Pencil size={16} />Editar</Link>{item.ativa && <button className="btn-secondary text-rose-700" onClick={() => deactivate(item)}><Ban size={16} />Desativar</button>}</div></div></article>)}</div></State></>;
}
