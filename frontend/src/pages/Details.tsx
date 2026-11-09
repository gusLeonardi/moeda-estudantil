
import {
  ArrowDownLeft,
  ArrowLeft,
  ArrowUpRight,
  Building2,
  GraduationCap,
  History,
  Mail,
  Pencil,
  Phone,
  RefreshCw,
} from 'lucide-react';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { PageHeader, State } from '../components/UI';
import { useAsync } from '../hooks/useAsync';
import { alunoService } from '../services/alunoService';
import { empresaService } from '../services/empresaService';
import { apiMessage } from '../services/api';

function Row({
  label,
  value,
}: {
  label: string;
  value: string;
}) {
  return (
    <div className="border-b border-slate-100 py-4 last:border-0">
      <dt className="text-xs font-bold uppercase tracking-wider text-slate-400">
        {label}
      </dt>
      <dd className="mt-1 font-medium text-slate-800">{value}</dd>
    </div>
  );
}

type Movimentacao = Record<string, unknown>;

function texto(valor: unknown): string {
  if (valor === null || valor === undefined) return '';
  if (typeof valor === 'string' || typeof valor === 'number') {
    return String(valor);
  }
  return '';
}

function numero(valor: unknown): number {
  const n = Number(valor);
  return Number.isFinite(n) ? n : 0;
}

function formatarData(valor: unknown): string {
  if (!valor) return 'Data não informada';

  const data = new Date(String(valor));

  if (Number.isNaN(data.getTime())) {
    return String(valor);
  }

  return data.toLocaleString('pt-BR');
}

function obterMovimentacoes(resposta: unknown): Movimentacao[] {
  if (Array.isArray(resposta)) {
    return resposta.filter(
      (item): item is Movimentacao =>
        typeof item === 'object' && item !== null
    );
  }

  if (typeof resposta !== 'object' || resposta === null) {
    return [];
  }

  const objeto = resposta as Record<string, unknown>;

  if (Array.isArray(objeto.movimentos)) {
    return obterMovimentacoes(objeto.movimentos);
  }

  return [];
}

function HistoricoAluno({ alunoId }: { alunoId: number }) {
  const [movimentacoes, setMovimentacoes] = useState<Movimentacao[]>([]);
  const [loading, setLoading] = useState(true);
  const [erro, setErro] = useState('');

  const carregar = async () => {
    setLoading(true);
    setErro('');

    try {
      const resposta = await alunoService.extrato(alunoId);
      setMovimentacoes(obterMovimentacoes(resposta));
    } catch (error) {
      setErro(apiMessage(error));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    let ativo = true;

    setLoading(true);
    setErro('');

    alunoService
      .extrato(alunoId)
      .then((resposta) => {
        if (ativo) {
          setMovimentacoes(obterMovimentacoes(resposta));
        }
      })
      .catch((error) => {
        if (ativo) setErro(apiMessage(error));
      })
      .finally(() => {
        if (ativo) setLoading(false);
      });

    return () => {
      ativo = false;
    };
  }, [alunoId]);

  return (
    <section className="card mt-5 p-5 sm:p-7">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <History size={22} className="text-blue-700" />
            <h2 className="text-xl font-bold text-slate-900">
              Histórico de movimentações
            </h2>
          </div>
          <p className="mt-1 text-sm text-slate-500">
            Moedas recebidas e vantagens resgatadas pelo aluno.
          </p>
        </div>

        <button
          type="button"
          className="btn-secondary"
          onClick={carregar}
          disabled={loading}
        >
          <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
          Atualizar
        </button>
      </div>

      {loading ? (
        <div className="mt-6 rounded-xl bg-slate-50 p-5 text-sm text-slate-500">
          Carregando movimentações...
        </div>
      ) : erro ? (
        <div className="mt-6 rounded-xl bg-rose-50 p-4 text-sm text-rose-700">
          Não foi possível carregar o extrato: {erro}
        </div>
      ) : movimentacoes.length === 0 ? (
        <div className="mt-6 rounded-xl bg-slate-50 p-6 text-center">
          <History size={28} className="mx-auto text-slate-400" />
          <p className="mt-2 font-medium text-slate-700">
            Nenhuma movimentação encontrada.
          </p>
          <p className="mt-1 text-sm text-slate-500">
            As transferências e os resgates aparecerão aqui.
          </p>
        </div>
      ) : (
        <div className="mt-6 divide-y divide-slate-100">
          {movimentacoes.map((mov, index) => {
            const tipo = texto(
              mov.tipo ?? mov.tipo_movimentacao ?? mov.operacao
            ).toLowerCase();

            const saida =
              tipo.includes('resgate') ||
              tipo.includes('debito') ||
              tipo.includes('débito') ||
              tipo.includes('saida') ||
              tipo.includes('saída');

            const quantidade = numero(
              mov.quantidade ?? mov.valor ?? mov.moedas
            );

            const descricao =
              texto(
                mov.justificativa ??
                  mov.descricao ??
                  mov.vantagem_nome ??
                  mov.vantagem
              ) || (saida ? 'Resgate de vantagem' : 'Recebimento de moedas');

            const origem = texto(
              mov.professor_nome ??
                mov.professor ??
                mov.remetente_nome
            );

            const data =
              mov.criado_em ??
              mov.data ??
              mov.data_hora ??
              mov.created_at;

            return (
              <div
                key={texto(mov.id) || index}
                className="flex items-start gap-4 py-5"
              >
                <span
                  className={`grid h-11 w-11 shrink-0 place-items-center rounded-xl ${
                    saida
                      ? 'bg-rose-50 text-rose-700'
                      : 'bg-teal-50 text-teal-700'
                  }`}
                >
                  {saida ? (
                    <ArrowUpRight size={21} />
                  ) : (
                    <ArrowDownLeft size={21} />
                  )}
                </span>

                <div className="min-w-0 flex-1">
                  <p className="font-bold text-slate-900">
                    {saida ? 'Resgate de vantagem' : 'Moedas recebidas'}
                  </p>

                  <p className="mt-1 text-sm text-slate-600">
                    {descricao}
                  </p>

                  {origem && (
                    <p className="mt-1 text-xs text-slate-500">
                      Professor: {origem}
                    </p>
                  )}

                  <p className="mt-2 text-xs text-slate-400">
                    {formatarData(data)}
                  </p>
                </div>

                <span
                  className={`whitespace-nowrap font-extrabold ${
                    saida ? 'text-rose-700' : 'text-teal-700'
                  }`}
                >
                  {saida ? '-' : '+'}
                  {Math.abs(quantidade).toFixed(2)}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export function AlunoDetail() {
  const { id } = useParams();
  const state = useAsync(() => alunoService.obter(Number(id)), [id]);
  const x = state.data;

  return (
    <>
      <PageHeader
        eyebrow="Perfil acadêmico"
        title={x?.nome || 'Detalhes do aluno'}
        description="Informações cadastrais e movimentações do estudante."
        action={
          <Link to={`/alunos/${id}/editar`} className="btn-primary">
            <Pencil size={17} />
            Editar
          </Link>
        }
      />

      <State loading={state.loading} error={state.error} empty={!x}>
        {x && (
          <>
            <div className="grid gap-5 lg:grid-cols-3">
              <div className="card p-6">
                <span className="grid h-14 w-14 place-items-center rounded-2xl bg-blue-50 text-blue-700">
                  <GraduationCap />
                </span>

                <h2 className="mt-5 text-xl font-bold">{x.nome}</h2>

                <p className="mt-1 flex items-center gap-2 text-sm text-slate-500">
                  <Mail size={15} />
                  {x.email}
                </p>

                <div className="mt-5 rounded-xl bg-teal-50 p-4">
                  <small className="font-bold text-teal-700">
                    SALDO ATUAL
                  </small>

                  <p className="text-2xl font-extrabold text-teal-800">
                    {Number(x.saldo).toFixed(2)} moedas
                  </p>
                </div>
              </div>

              <dl className="card p-6 lg:col-span-2">
                <Row label="CPF" value={x.cpf} />
                <Row label="RG" value={x.rg} />
                <Row label="Curso" value={x.curso} />
                <Row
                  label="Instituição"
                  value={`${x.instituicao.sigla} · ${x.instituicao.nome}`}
                />
                <Row
                  label="Endereço"
                  value={`${x.endereco.logradouro}, ${x.endereco.numero}${
                    x.endereco.complemento
                      ? ` · ${x.endereco.complemento}`
                      : ''
                  } · ${x.endereco.bairro}, ${x.endereco.cidade}/${
                    x.endereco.estado
                  } · CEP ${x.endereco.cep}`}
                />
              </dl>
            </div>

            <HistoricoAluno alunoId={Number(id)} />
          </>
        )}
      </State>

      <Link to="/alunos" className="btn-secondary mt-5">
        <ArrowLeft size={17} />
        Voltar
      </Link>
    </>
  );
}

export function EmpresaDetail() {
  const { id } = useParams();
  const state = useAsync(() => empresaService.obter(Number(id)), [id]);
  const x = state.data;

  return (
    <>
      <PageHeader
        eyebrow="Perfil parceiro"
        title={x?.nome || 'Detalhes da empresa'}
        description="Informações da organização parceira."
        action={
          <Link to={`/empresas/${id}/editar`} className="btn-primary">
            <Pencil size={17} />
            Editar
          </Link>
        }
      />

      <State loading={state.loading} error={state.error} empty={!x}>
        {x && (
          <div className="grid gap-5 lg:grid-cols-3">
            <div className="card p-6">
              <span className="grid h-14 w-14 place-items-center rounded-2xl bg-blue-50 text-blue-700">
                <Building2 />
              </span>

              <h2 className="mt-5 text-xl font-bold">{x.nome}</h2>

              <p className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                <Mail size={15} />
                {x.email}
              </p>

              <p className="mt-2 flex items-center gap-2 text-sm text-slate-500">
                <Phone size={15} />
                {x.telefone}
              </p>
            </div>

            <dl className="card p-6 lg:col-span-2">
              <Row label="CNPJ" value={x.cnpj} />
              <Row label="E-mail" value={x.email} />
              <Row label="Telefone" value={x.telefone} />
              <Row
                label="Endereço"
                value={`${x.endereco.logradouro}, ${x.endereco.numero}${
                  x.endereco.complemento
                    ? ` · ${x.endereco.complemento}`
                    : ''
                } · ${x.endereco.bairro}, ${x.endereco.cidade}/${
                  x.endereco.estado
                } · CEP ${x.endereco.cep}`}
              />
            </dl>
          </div>
        )}
      </State>

      <Link to="/empresas" className="btn-secondary mt-5">
        <ArrowLeft size={17} />
        Voltar
      </Link>
    </>
  );
}
