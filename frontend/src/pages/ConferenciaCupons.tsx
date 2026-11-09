
import { useEffect, useState, type FormEvent } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronDown,
  ClipboardCheck,
  Loader2,
  RefreshCw,
  Search,
  TicketCheck,
} from 'lucide-react';

import { api, apiMessage } from '../services/api';
import {
  consultarCupom,
  validarCupom,
  type CupomConferencia,
} from '../services/cupons';

interface Empresa {
  id: number;
  nome: string;
}

interface EmpresaApi {
  id?: number;
  usuario_id?: number;
  nome?: string;
  usuario?: {
    nome?: string;
  };
}

export function ConferenciaCupons() {
  const [empresas, setEmpresas] = useState<Empresa[]>([]);
  const [empresaId, setEmpresaId] = useState('');
  const [codigoCupom, setCodigoCupom] = useState('');

  const [cupom, setCupom] = useState<CupomConferencia | null>(null);

  const [carregandoEmpresas, setCarregandoEmpresas] = useState(true);
  const [carregando, setCarregando] = useState(false);
  const [validando, setValidando] = useState(false);

  const [erroEmpresas, setErroEmpresas] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');

  const limparResultado = () => {
    setCupom(null);
    setErro('');
    setSucesso('');
  };

  const carregarEmpresas = async () => {
    setCarregandoEmpresas(true);
    setErroEmpresas('');

    try {
      const response = await api.get<EmpresaApi[]>('/empresas');

      const lista = response.data
        .map((empresa) => ({
          id: Number(empresa.id ?? empresa.usuario_id),
          nome: empresa.nome ?? empresa.usuario?.nome ?? '',
        }))
        .filter(
          (empresa) =>
            Number.isSafeInteger(empresa.id) &&
            empresa.id > 0 &&
            empresa.nome.trim().length > 0,
        )
        .sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'));

      setEmpresas(lista);

      if (
        empresaId &&
        !lista.some((empresa) => String(empresa.id) === empresaId)
      ) {
        setEmpresaId('');
        limparResultado();
      }
    } catch (error) {
      setEmpresas([]);
      setErroEmpresas(apiMessage(error));
    } finally {
      setCarregandoEmpresas(false);
    }
  };

  useEffect(() => {
    void carregarEmpresas();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const consultar = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    limparResultado();

    const id = Number(empresaId);
    const codigo = codigoCupom.trim().toUpperCase();

    if (!Number.isSafeInteger(id) || id <= 0) {
      setErro('Selecione uma empresa parceira.');
      return;
    }

    if (!codigo) {
      setErro('Informe o código do cupom.');
      return;
    }

    setCarregando(true);

    try {
      const resultado = await consultarCupom({
        empresa_id: id,
        codigo_cupom: codigo,
      });

      setCupom(resultado);
    } catch (error) {
      setErro(apiMessage(error));
    } finally {
      setCarregando(false);
    }
  };

  const validar = async () => {
    if (!cupom || cupom.utilizado) {
      return;
    }

    const confirmado = window.confirm(
      `Deseja confirmar a utilização do cupom ${cupom.codigo_cupom}? Essa ação não poderá ser desfeita.`,
    );

    if (!confirmado) {
      return;
    }

    setErro('');
    setSucesso('');
    setValidando(true);

    try {
      const resultado = await validarCupom({
        empresa_id: cupom.empresa_id,
        codigo_cupom: cupom.codigo_cupom,
      });

      setCupom(resultado);
      setSucesso(resultado.mensagem);
    } catch (error) {
      setErro(apiMessage(error));

      try {
        const atualizado = await consultarCupom({
          empresa_id: cupom.empresa_id,
          codigo_cupom: cupom.codigo_cupom,
        });

        setCupom(atualizado);
      } catch {
        setCupom(null);
      }
    } finally {
      setValidando(false);
    }
  };

  const formatarData = (valor: string) =>
    new Date(valor).toLocaleString('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    });

  const nomeEmpresa = (id: number) =>
    empresas.find((empresa) => empresa.id === id)?.nome ??
    `Empresa #${id}`;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <div className="rounded-xl bg-emerald-100 p-3 text-emerald-700">
          <TicketCheck size={25} />
        </div>

        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Conferência de Cupons
          </h1>

          <p className="text-sm text-slate-500">
            Consulte e valide os cupons apresentados pelos alunos.
          </p>
        </div>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-slate-900">
            Consultar cupom
          </h2>

          <button
            type="button"
            onClick={() => void carregarEmpresas()}
            disabled={carregandoEmpresas}
            className="flex items-center gap-2 rounded-lg px-3 py-2 text-sm font-medium text-slate-600 transition hover:bg-slate-100 disabled:opacity-50"
          >
            <RefreshCw
              size={16}
              className={carregandoEmpresas ? 'animate-spin' : ''}
            />
            Atualizar empresas
          </button>
        </div>

        <form onSubmit={consultar} className="space-y-5">
          <div className="grid gap-5 md:grid-cols-2">
            <div>
              <label
                htmlFor="empresa-id"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Empresa parceira
              </label>

              <div className="relative">
                <select
                  id="empresa-id"
                  required
                  value={empresaId}
                  disabled={carregandoEmpresas || validando}
                  onChange={(event) => {
                    setEmpresaId(event.target.value);
                    limparResultado();
                  }}
                  className="w-full appearance-none rounded-xl border border-slate-300 bg-white px-4 py-3 pr-10 text-slate-900 outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100"
                >
                  <option value="">
                    {carregandoEmpresas
                      ? 'Carregando empresas...'
                      : 'Selecione uma empresa'}
                  </option>

                  {empresas.map((empresa) => (
                    <option key={empresa.id} value={empresa.id}>
                      {empresa.nome}
                    </option>
                  ))}
                </select>

                <ChevronDown
                  size={18}
                  className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-500"
                />
              </div>

              {erroEmpresas && (
                <p className="mt-2 text-sm text-red-600" role="alert">
                  {erroEmpresas}
                </p>
              )}

              {!carregandoEmpresas &&
                !erroEmpresas &&
                empresas.length === 0 && (
                  <p className="mt-2 text-sm text-amber-700">
                    Nenhuma empresa cadastrada foi encontrada.
                  </p>
                )}
            </div>

            <div>
              <label
                htmlFor="codigo-cupom"
                className="mb-2 block text-sm font-medium text-slate-700"
              >
                Código do cupom
              </label>

              <input
                id="codigo-cupom"
                type="text"
                maxLength={32}
                required
                value={codigoCupom}
                disabled={validando}
                onChange={(event) => {
                  setCodigoCupom(event.target.value.toUpperCase());
                  limparResultado();
                }}
                placeholder="Digite o código do cupom"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 font-mono uppercase outline-none transition focus:border-emerald-500 focus:ring-2 focus:ring-emerald-100 disabled:bg-slate-100"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={
              carregando ||
              validando ||
              carregandoEmpresas ||
              empresas.length === 0
            }
            className="flex items-center justify-center gap-2 rounded-xl bg-navy px-6 py-3 font-semibold text-white transition hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {carregando ? (
              <Loader2 size={19} className="animate-spin" />
            ) : (
              <Search size={19} />
            )}

            {carregando ? 'Consultando...' : 'Consultar cupom'}
          </button>
        </form>
      </div>

      {erro && (
        <div
          role="alert"
          className="flex items-start gap-3 rounded-xl border border-red-200 bg-red-50 p-4 text-red-700"
        >
          <AlertCircle size={21} className="mt-0.5 shrink-0" />
          <p>{erro}</p>
        </div>
      )}

      {sucesso && (
        <div
          role="status"
          className="flex items-start gap-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4 text-emerald-800"
        >
          <CheckCircle2 size={21} className="mt-0.5 shrink-0" />
          <p>{sucesso}</p>
        </div>
      )}

      {cupom && (
        <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 p-6">
            <div>
              <h2 className="text-lg font-bold text-slate-900">
                Dados do cupom
              </h2>

              <p className="mt-1 font-mono text-sm text-slate-500">
                {cupom.codigo_cupom}
              </p>
            </div>

            <span
              className={`rounded-full px-4 py-2 text-sm font-semibold ${
                cupom.utilizado
                  ? 'bg-slate-100 text-slate-700'
                  : 'bg-emerald-100 text-emerald-800'
              }`}
            >
              {cupom.utilizado ? 'Já utilizado' : 'Disponível'}
            </span>
          </div>

          <div className="grid gap-6 p-6 sm:grid-cols-2">
            <div>
              <p className="text-sm text-slate-500">Vantagem</p>
              <p className="mt-1 font-semibold text-slate-900">
                {cupom.vantagem_nome}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Custo do resgate
              </p>
              <p className="mt-1 font-semibold text-slate-900">
                {Number(cupom.custo).toLocaleString('pt-BR', {
                  maximumFractionDigits: 2,
                })}{' '}
                moedas
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">Aluno</p>
              <p className="mt-1 font-semibold text-slate-900">
                #{cupom.aluno_id}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">Empresa</p>
              <p className="mt-1 font-semibold text-slate-900">
                {nomeEmpresa(cupom.empresa_id)}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500">
                Data do resgate
              </p>
              <p className="mt-1 font-semibold text-slate-900">
                {formatarData(cupom.criado_em)}
              </p>
            </div>

            {cupom.utilizado_em && (
              <div>
                <p className="text-sm text-slate-500">
                  Utilizado em
                </p>
                <p className="mt-1 font-semibold text-slate-900">
                  {formatarData(cupom.utilizado_em)}
                </p>
              </div>
            )}
          </div>

          <div className="border-t border-slate-200 bg-slate-50 p-6">
            {cupom.utilizado ? (
              <div className="flex items-center gap-3 text-slate-600">
                <ClipboardCheck size={22} />

                <p className="font-medium">
                  Este cupom já foi utilizado e não pode ser
                  validado novamente.
                </p>
              </div>
            ) : (
              <button
                type="button"
                onClick={validar}
                disabled={validando}
                style={{
                  backgroundColor: validando ? '#86efac' : '#16a34a',
                  color: '#ffffff',
                  boxShadow: validando
                    ? 'none'
                    : '0 4px 14px rgba(22, 163, 74, 0.30)',
                }}
                onMouseEnter={(event) => {
                  if (!validando) {
                    event.currentTarget.style.backgroundColor = '#15803d';
                  }
                }}
                onMouseLeave={(event) => {
                  if (!validando) {
                    event.currentTarget.style.backgroundColor = '#16a34a';
                  }
                }}
                className="flex items-center justify-center gap-2 rounded-xl px-6 py-3 font-bold transition-all duration-200 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {validando ? (
                  <Loader2 size={20} className="animate-spin" />
                ) : (
                  <CheckCircle2 size={20} />
                )}

                {validando
                  ? 'Validando cupom...'
                  : 'Confirmar utilização'}
              </button>
            )}
          </div>
        </div>
      )}

      <p className="text-sm text-slate-500">
        Ambiente de demonstração acadêmica. A empresa é selecionada
        manualmente enquanto a autenticação não está implementada.
      </p>
    </div>
  );
}
