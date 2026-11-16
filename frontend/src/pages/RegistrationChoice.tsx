import { ArrowLeft, ArrowRight, Building2, GraduationCap, School, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';

const profiles = [
  { role: 'Aluno', detail: 'Receba moedas, acompanhe seu saldo e troque por vantagens.', to: '/cadastro/aluno', Icon: GraduationCap, tone: 'bg-blue-50 text-blue-800', badge: 'Comunidade acadêmica' },
  { role: 'Professor', detail: 'Participe da jornada dos alunos e distribua reconhecimento.', to: '/cadastro/professor', Icon: School, tone: 'bg-violet-50 text-violet-800', badge: 'Educador' },
  { role: 'Empresa parceira', detail: 'Publique vantagens e receba alunos na sua empresa.', to: '/cadastro/empresa', Icon: Building2, tone: 'bg-teal-50 text-teal-800', badge: 'Parceiro local' },
];

export function RegistrationChoice() {
  return <main className="min-h-[calc(100vh-2rem)] bg-slate-50 px-4 py-8 sm:grid sm:place-items-center sm:py-12">
    <div className="w-full max-w-5xl">
      <Link className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 transition hover:text-blue-800" to="/login"><ArrowLeft size={16} /> Voltar ao login</Link>
      <section className="mt-6 overflow-hidden rounded-[2rem] border border-slate-200 bg-white shadow-xl shadow-slate-200/60">
        <div className="bg-gradient-to-r from-blue-950 via-blue-900 to-teal-800 px-6 py-10 text-white sm:px-10 sm:py-12">
          <span className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/10 px-3 py-1.5 text-xs font-bold uppercase tracking-wider text-teal-100"><ShieldCheck size={15} /> Cadastro gratuito</span>
          <h1 className="mt-5 text-3xl font-extrabold tracking-tight sm:text-4xl">Faça parte do Conquista</h1>
          <p className="mt-3 max-w-2xl leading-7 text-blue-100">Escolha como você participa da comunidade. Você poderá entrar na sua conta assim que concluir o cadastro.</p>
        </div>
        <div className="grid gap-4 p-5 sm:grid-cols-3 sm:p-8">
          {profiles.map(({ role, detail, to, Icon, tone, badge }) => <Link key={role} to={to} className="group flex min-h-64 flex-col rounded-2xl border border-slate-200 bg-white p-5 transition duration-200 hover:-translate-y-1 hover:border-blue-200 hover:shadow-lg hover:shadow-blue-950/5 focus:outline-none focus:ring-4 focus:ring-blue-100 sm:p-6">
            <span className={`grid h-12 w-12 place-items-center rounded-2xl ${tone}`}><Icon size={24} /></span>
            <span className="mt-5 text-xs font-bold uppercase tracking-wider text-slate-400">{badge}</span>
            <span className="mt-1 text-xl font-extrabold text-slate-950">{role}</span>
            <span className="mt-2 flex-1 text-sm leading-6 text-slate-500">{detail}</span>
            <span className="mt-5 inline-flex items-center gap-2 font-bold text-blue-800">Começar cadastro <ArrowRight size={17} className="transition group-hover:translate-x-1" /></span>
          </Link>)}
        </div>
        <p className="border-t border-slate-100 px-6 py-4 text-center text-sm text-slate-500">Já tem uma conta? <Link className="font-bold text-blue-800 underline underline-offset-4" to="/login">Entrar</Link></p>
      </section>
    </div>
  </main>;
}
