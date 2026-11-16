import { Ban, Check, Pencil, Plus, Trash2 } from 'lucide-react';
import { useCallback, useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { readSession } from '../auth/session';
import { PageHeader, State } from '../components/UI';
import { apiMessage } from '../services/api';
import { vantagemService } from '../services/vantagemService';
import type { Vantagem } from '../types';

export function VantagemList() {
  const session = readSession();
  const [items, setItems] = useState<Vantagem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const mine = await vantagemService.minhas();
      setItems(mine.filter(item => item.empresa_id === session?.id));
      setError('');
    } catch (cause) { setError(apiMessage(cause)); }
    finally { setLoading(false); }
  }, [session?.id]);

  useEffect(() => { void load(); }, [load]);

  const setStatus = async (item: Vantagem) => {
    try {
      if (item.ativa) await vantagemService.desativar(item.id);
      else await vantagemService.ativar(item.id);
      await load();
    } catch (cause) { setError(apiMessage(cause)); }
  };

  const remove = async (item: Vantagem) => {
    if (!window.confirm(`Excluir ${item.nome}? Vantagens com histórico de resgates devem ser desativadas.`)) return;
    try { await vantagemService.excluir(item.id); await load(); }
    catch (cause) { setError(apiMessage(cause)); }
  };

  return <>
    <PageHeader eyebrow="Área da empresa" title="Minhas vantagens" description="Gerencie somente benefícios cadastrados pela sua empresa." action={<Link className="btn-primary" to="/vantagens/nova"><Plus size={18} />Nova vantagem</Link>} />
    <State loading={loading} error={error} empty={!items.length}>
      <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{items.map(item => <article key={item.id} className="card overflow-hidden">
        {item.imagem_url ? <img src={item.imagem_url} alt="" className="h-40 w-full bg-slate-100 object-cover" /> : <div className="grid h-40 place-items-center bg-slate-100 text-slate-400">Sem imagem</div>}
        <div className="p-5"><div className="flex items-start justify-between gap-3"><div><h2 className="font-bold">{item.nome}</h2><p className="text-sm text-slate-500">{item.empresa_nome}</p></div><span className={`rounded-full px-2 py-1 text-xs font-bold ${item.ativa ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-500'}`}>{item.ativa ? 'Ativa' : 'Inativa'}</span></div>
          <p className="mt-3 text-sm text-slate-600">{item.descricao}</p><p className="mt-4 text-xl font-extrabold text-teal-700">{Number(item.custo).toFixed(2)} moedas</p>
          {item.empresa_id === session?.id && <div className="mt-4 flex flex-wrap gap-2"><Link className="btn-secondary" to={`/vantagens/${item.id}/editar`}><Pencil size={16} />Editar</Link><button className="btn-secondary" onClick={() => void setStatus(item)}>{item.ativa ? <Ban size={16} /> : <Check size={16} />}{item.ativa ? 'Desativar' : 'Ativar'}</button><button className="btn-secondary text-rose-700" onClick={() => void remove(item)}><Trash2 size={16} />Excluir</button></div>}
        </div>
      </article>)}</div>
    </State>
  </>;
}
