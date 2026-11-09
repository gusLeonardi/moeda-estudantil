import { Eye, Plus } from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { PageHeader, SearchBox, State } from '../components/UI';
import { apiMessage } from '../services/api';
import { professorService } from '../services/professorService';
import type { Professor } from '../types';

export function ProfessorList() {
  const [items, setItems] = useState<Professor[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  useEffect(() => {
    const timer = setTimeout(() => {
      setLoading(true); setError('');
      professorService.listar(query).then(setItems).catch(error => setError(apiMessage(error))).finally(() => setLoading(false));
    }, 250);
    return () => clearTimeout(timer);
  }, [query]);
  return <>
    <PageHeader eyebrow="Fluxo administrativo de demonstração" title="Professores" description="Professores pré-cadastrados, saldos e distribuição de moedas." action={<Link to="/professores/novo" className="btn-primary"><Plus size={18} />Novo professor</Link>} />
    <div className="mb-5 rounded-xl bg-amber-50 p-4 text-sm text-amber-800">Ambiente sem autenticação. Use este fluxo somente localmente para demonstração.</div>
    <div className="card mb-5 p-4"><SearchBox value={query} onChange={setQuery} placeholder="Buscar por nome, CPF, e-mail ou departamento" /></div>
    <State loading={loading} error={error} empty={!items.length}><div className="card overflow-x-auto"><table className="w-full min-w-[720px] text-left"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="px-5 py-4">Professor</th><th>Departamento</th><th>Instituição</th><th>Saldo</th><th className="px-5 text-right">Ação</th></tr></thead><tbody className="divide-y divide-slate-100">{items.map(item => <tr key={item.id}><td className="px-5 py-4"><b className="block">{item.nome}</b><small>{item.email}</small></td><td>{item.departamento}</td><td>{item.instituicao.sigla}</td><td className="font-bold text-teal-700">{Number(item.saldo).toFixed(2)}</td><td className="px-5 text-right"><Link className="btn-secondary !p-2" to={`/professores/${item.id}`} aria-label={`Abrir ${item.nome}`}><Eye size={17} /></Link></td></tr>)}</tbody></table></div></State>
  </>;
}
