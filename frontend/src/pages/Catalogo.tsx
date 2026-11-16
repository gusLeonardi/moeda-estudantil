import { Gift, TicketCheck } from 'lucide-react';
import { useEffect, useState } from 'react';
import { readSession } from '../auth/session';
import { PageHeader, State } from '../components/UI';
import { alunoService } from '../services/alunoService';
import { apiMessage } from '../services/api';
import { vantagemService } from '../services/vantagemService';
import type { ExtratoAluno, Resgate, Vantagem } from '../types';

export function Catalogo() {
  const session = readSession();
  const studentId = session?.tipo === 'ALUNO' ? session.id : 0;
  const [vantagens, setVantagens] = useState<Vantagem[]>([]);
  const [extrato, setExtrato] = useState<ExtratoAluno | null>(null);
  const [cupom, setCupom] = useState<Resgate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [processing, setProcessing] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([vantagemService.catalogo(), alunoService.extrato(studentId)])
      .then(([items, statement]) => { setVantagens(items); setExtrato(statement); })
      .catch(err => setError(apiMessage(err)))
      .finally(() => setLoading(false));
  }, [studentId]);

  const redeem = async (item: Vantagem) => {
    if (!studentId) return;
    setProcessing(item.id); setError('');
    try {
      const key = crypto.randomUUID().replace(/-/g, '');
      const result = await vantagemService.resgatar(item.id, key);
      setCupom(result); setExtrato(await alunoService.extrato(studentId));
    } catch (err) { setError(apiMessage(err)); }
    finally { setProcessing(null); }
  };

  return <>
    <PageHeader eyebrow="Área do aluno" title="Catálogo de vantagens" description="Use suas moedas para resgatar benefícios disponíveis para você." />
    {extrato && <section className="mb-6 flex flex-wrap items-center justify-between gap-3 rounded-2xl bg-gradient-to-r from-teal-700 to-blue-800 p-5 text-white"><div><p className="text-sm text-teal-100">Meu saldo disponível</p><p className="mt-1 text-3xl font-extrabold">{Number(extrato.saldo).toFixed(2)} <span className="text-base font-semibold">moedas</span></p></div><Gift className="text-teal-200" size={34} /></section>}
    {error && <p role="alert" className="mb-5 rounded-xl bg-rose-50 p-3 text-sm text-rose-700">{error}</p>}
    <State loading={loading} error="" empty={!vantagens.length}><div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">{vantagens.map(item => <article className="card overflow-hidden" key={item.id}>{item.imagem_url ? <img src={item.imagem_url} alt={item.nome} className="h-48 w-full bg-slate-100 object-cover" /> : <div className="grid h-48 place-items-center bg-slate-100"><Gift className="text-slate-400" /></div>}<div className="p-5"><h2 className="font-bold">{item.nome}</h2><p className="text-sm text-slate-500">{item.empresa_nome}</p><p className="mt-3 text-sm leading-6 text-slate-600">{item.descricao}</p><div className="mt-4 flex items-center justify-between gap-3"><p className="text-lg font-extrabold text-teal-700">{Number(item.custo).toFixed(2)} moedas</p><button className="btn-primary" disabled={!extrato || processing === item.id || Number(extrato.saldo) < Number(item.custo)} onClick={() => redeem(item)}>{processing === item.id ? 'Resgatando...' : 'Resgatar'}</button></div></div></article>)}</div></State>
    {extrato && <section className="card mt-6 overflow-x-auto"><h2 className="p-5 text-xl font-bold">Meu extrato</h2>{!extrato.movimentos.length ? <p className="px-5 pb-5 text-slate-500">Nenhuma movimentação.</p> : <table className="w-full min-w-[700px] text-left"><thead className="bg-slate-50 text-xs uppercase text-slate-500"><tr><th className="px-5 py-3">Data</th><th>Tipo</th><th>Descrição</th><th>Valor</th><th>Cupom</th></tr></thead><tbody>{extrato.movimentos.map((item, index) => <tr className="border-t" key={`${item.data}-${index}`}><td className="px-5 py-3">{new Date(item.data).toLocaleString('pt-BR')}</td><td>{item.tipo}</td><td>{item.descricao}</td><td>{Number(item.quantidade).toFixed(2)}</td><td>{item.codigo_cupom || '—'}</td></tr>)}</tbody></table>}</section>}
    {cupom && <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/50 p-4"><div role="dialog" aria-modal="true" className="card max-w-md p-7 text-center"><TicketCheck className="mx-auto text-teal-600" size={48} /><h2 className="mt-4 text-2xl font-bold">Resgate concluído</h2><p className="mt-2">{cupom.vantagem_nome}</p><p className="mt-5 rounded-xl bg-slate-100 p-4 font-mono text-2xl font-bold tracking-widest">{cupom.codigo_cupom}</p><p className="mt-3 text-sm text-slate-500">Apresente este código à empresa parceira e confira o e-mail cadastrado.</p><button className="btn-primary mt-5" onClick={() => setCupom(null)}>Fechar</button></div></div>}
  </>;
}
