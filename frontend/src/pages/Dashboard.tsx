import { ArrowRight, Building2, Gift, GraduationCap, School, ShoppingBag, Sparkles, TicketCheck, type LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { readSession } from '../auth/session';
import { PageHeader, State } from '../components/UI';
import { useAsync } from '../hooks/useAsync';
import { dashboardService } from '../services/dashboardService';

type DashboardCard = { title: string; count?: number; icon: LucideIcon; description: string; to: string };

export function Dashboard() {
  const session = readSession();
  const professor = session?.tipo === 'PROFESSOR';
  const indicators = useAsync(() => professor ? dashboardService.obterIndicadores() : Promise.resolve(null), [professor]);
  const cards: DashboardCard[] = session?.tipo === 'ADMIN' ? [
    { title: 'Gerenciar professores', icon: School, description: 'Pré-cadastre docentes, confira os dados e acompanhe a ativação das contas.', to: '/admin/professores' },
  ] : session?.tipo === 'ALUNO' ? [
    { title: 'Meu perfil acadêmico', icon: GraduationCap, description: 'Consulte seus dados e acompanhe sua trajetória.', to: '/alunos' },
    { title: 'Catálogo de vantagens', icon: ShoppingBag, description: 'Explore benefícios e consulte seus resgates.', to: '/catalogo' },
  ] : session?.tipo === 'EMPRESA' ? [
    { title: 'Minha empresa', icon: Building2, description: 'Revise os dados da sua conta parceira.', to: '/empresas' },
    { title: 'Minhas vantagens', icon: Gift, description: 'Gerencie os benefícios oferecidos aos alunos.', to: '/vantagens' },
    { title: 'Conferir cupons', icon: TicketCheck, description: 'Consulte e valide cupons apresentados pelos alunos.', to: '/cupons' },
  ] : [
    { title: 'Alunos', count: indicators.data?.total_alunos, icon: GraduationCap, description: 'Consulte alunos para reconhecer suas conquistas.', to: '/alunos' },
    { title: 'Meu perfil de professor', icon: School, description: 'Consulte seu saldo e histórico de distribuições.', to: '/professores' },
  ];

  return <>
    <PageHeader eyebrow="Sistema de reconhecimento" title={`Olá, ${session?.nome ?? 'bem-vindo'}!`} description="Acesse as ferramentas disponíveis para o seu perfil no Conquista." />
    <section className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-navy via-blue-900 to-teal-800 p-7 text-white sm:p-10">
      <div className="max-w-2xl"><span className="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-bold"><Sparkles size={15} /> Reconhecimento que circula</span><h2 className="text-3xl font-extrabold sm:text-4xl">Conquistas que conectam a comunidade acadêmica.</h2><p className="mt-4 text-blue-100">Seu painel mostra apenas os recursos e informações disponíveis para o seu perfil.</p></div>
    </section>
    {professor ? <State loading={indicators.loading} error={indicators.error} empty={false}><Cards cards={cards} /></State> : <Cards cards={cards} />}
  </>;
}

function Cards({ cards }: { cards: DashboardCard[] }) {
  return <div className="grid gap-5 md:grid-cols-2">{cards.map(({ title, count, icon: Icon, description, to }) => <Link key={title} to={to} className="card group p-6 transition hover:-translate-y-1 hover:border-blue-200 focus-visible:ring-4 focus-visible:ring-blue-100"><div className="flex items-start justify-between"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-blue-50 text-blue-700"><Icon /></span><ArrowRight className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-blue-700" /></div><p className="mt-7 text-sm font-semibold text-slate-500">{title}</p>{count !== undefined && <p className="mt-1 text-3xl font-extrabold text-slate-950">{count}</p>}<p className="mt-3 text-sm text-slate-500">{description}</p></Link>)}</div>;
}
