import { useEffect, useState } from 'react';
import { PageHeader, SearchBox, State } from '../components/UI';
import { alunoService } from '../services/alunoService';
import { apiMessage } from '../services/api';
import type { Aluno } from '../types';

export function AlunoList() {
  const [items, setItems] = useState<Aluno[]>([]);
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setLoading(true);
      alunoService.listar(query)
        .then(setItems)
        .catch(cause => setError(apiMessage(cause)))
        .finally(() => setLoading(false));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [query]);

  return <>
    <PageHeader eyebrow="Comunidade acadêmica" title="Alunos" description="Consulte alunos da instituição para reconhecer suas conquistas." />
    <div className="card mb-5 p-4"><SearchBox value={query} onChange={setQuery} placeholder="Buscar por nome ou e-mail" /></div>
    <State loading={loading} error={error} empty={!items.length}>
      <div className="card overflow-x-auto"><table className="w-full min-w-[640px] text-left">
        <thead className="bg-slate-50 text-xs uppercase tracking-wider text-slate-500"><tr><th className="px-5 py-4">Aluno</th><th>Curso</th><th>Instituição</th><th>Saldo</th></tr></thead>
        <tbody className="divide-y divide-slate-100">{items.map(student => <tr key={student.id}>
          <td className="px-5 py-4"><b className="block text-slate-900">{student.nome}</b><small className="text-slate-500">{student.email}</small></td>
          <td>{student.curso}</td><td>{student.instituicao.sigla}</td><td>{Number(student.saldo).toFixed(2)} moedas</td>
        </tr>)}</tbody>
      </table></div>
    </State>
  </>;
}
