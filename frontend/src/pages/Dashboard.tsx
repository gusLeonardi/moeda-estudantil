import { ArrowRight, Building2, Gift, GraduationCap, School, Sparkles, type LucideIcon } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PageHeader, State } from '../components/UI';
import { useAsync } from '../hooks/useAsync';
import { dashboardService } from '../services/dashboardService';

type DashboardCard = { title: string; count?: number; icon: LucideIcon; description: string; to: string };

export function Dashboard() {
  const indicators = useAsync(() => dashboardService.obterIndicadores(), []);
  const cards: DashboardCard[] = [
    { title: 'Alunos', count: indicators.data?.total_alunos, icon: GraduationCap, description: 'Gerencie perfis acadêmicos, cursos e instituições.', to: '/alunos' },
    { title: 'Empresas parceiras', count: indicators.data?.total_empresas, icon: Building2, description: 'Organize a rede de empresas parceiras.', to: '/empresas' },
    { title: 'Professores', count: indicators.data?.total_professores, icon: School, description: 'Distribua moedas e acompanhe extratos.', to: '/professores' },
    { title: 'Vantagens', count: indicators.data?.total_vantagens, icon: Gift, description: 'Gerencie benefícios e resgates com cupom.', to: '/vantagens' },
  ];
  return <>
    <PageHeader eyebrow="Sistema de reconhecimento" title="Valorize quem transforma o campus" description="Gerencie a comunidade que participa do ecossistema de reconhecimento estudantil da PUC Minas." />
    <section className="mb-8 overflow-hidden rounded-3xl bg-gradient-to-br from-navy via-blue-900 to-blue-700 p-7 text-white sm:p-10">
      <div className="max-w-2xl"><span className="mb-5 inline-flex items-center gap-2 rounded-full bg-white/10 px-3 py-1.5 text-xs font-bold"><Sparkles size={15} /> Reconhecimento que circula</span><h2 className="text-3xl font-extrabold sm:text-4xl">Conectando mérito acadêmico a oportunidades reais.</h2><p className="mt-4 text-blue-100">Esta etapa consolida os cadastros de alunos, instituições e empresas parceiras.</p></div>
    </section>
    <State loading={indicators.loading} error={indicators.error} empty={false}><div className="grid gap-5 md:grid-cols-2">{cards.map(({ title, count, icon: Icon, description, to }) => <Link key={title} to={to} className="card group p-6 transition hover:-translate-y-1 hover:border-blue-200 focus-visible:ring-4 focus-visible:ring-blue-100"><div className="flex items-start justify-between"><span className="grid h-12 w-12 place-items-center rounded-2xl bg-blue-50 text-blue-700"><Icon /></span><ArrowRight className="text-slate-300 transition group-hover:translate-x-1 group-hover:text-blue-700" /></div><p className="mt-7 text-sm font-semibold text-slate-500">{title}</p><p className="mt-1 text-3xl font-extrabold text-slate-950">{count}</p><p className="mt-3 text-sm text-slate-500">{description}</p></Link>)}</div></State>
  </>;
}
