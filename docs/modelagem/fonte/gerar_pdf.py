"""Gera Lab03S01-modelagem-atualizada.pdf (reportlab).

Uso: python gerar_pdf.py [caminho_de_saida.pdf]
Requer: reportlab e as fontes Arial/Courier New do macOS (ver desenho.py).
"""
import os
import sys

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
                                PageTemplate, Paragraph, Spacer, Table, TableStyle)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from desenho import F, FB, FI, FM, IMPL_FILL, PART_FILL, GRID, INK  # noqa: E402
from diagramas import DiagramaCasosDeUso, DiagramaClasses, DiagramaComponentes  # noqa: E402

SAIDA = sys.argv[1] if len(sys.argv) > 1 else "Lab03S01-modelagem-atualizada.pdf"
VERDE, AMARELO, CINZA = IMPL_FILL, PART_FILL, colors.HexColor("#eef0f3")

# ---- estilos --------------------------------------------------------------------------
base = ParagraphStyle("base", fontName=F, fontSize=9.2, leading=12.6, textColor=INK, spaceAfter=4)
peq = ParagraphStyle("peq", parent=base, fontSize=7.6, leading=9.6, spaceAfter=0)
peqb = ParagraphStyle("peqb", parent=peq, fontName=FB)
h1 = ParagraphStyle("h1", parent=base, fontName=FB, fontSize=14, leading=18, spaceBefore=10, spaceAfter=6)
h2 = ParagraphStyle("h2", parent=base, fontName=FB, fontSize=10.8, leading=14, spaceBefore=8, spaceAfter=4)
leg = ParagraphStyle("leg", parent=base, fontName=FI, fontSize=8.2, alignment=TA_CENTER, spaceBefore=3, spaceAfter=8)
nota = ParagraphStyle("nota", parent=base, fontSize=8.2, leading=11, textColor=colors.HexColor("#3e4c59"))
item = ParagraphStyle("item", parent=base, leftIndent=12, bulletIndent=2, spaceAfter=2)
tit = ParagraphStyle("tit", parent=base, fontName=FB, fontSize=21, leading=26, alignment=TA_CENTER, spaceAfter=6)
sub = ParagraphStyle("sub", parent=base, fontSize=11.5, leading=16, alignment=TA_CENTER, spaceAfter=3)
us_t = ParagraphStyle("us_t", parent=base, fontName=FB, spaceBefore=5, spaceAfter=1)
us_b = ParagraphStyle("us_b", parent=base, leftIndent=10, spaceAfter=1)


def P(t, s=base): return Paragraph(t, s)
def H1(t): return Paragraph(t, h1)
def H2(t): return Paragraph(t, h2)
def code(t): return '<font name="%s" size="8.6">%s</font>' % (FM, t)


def tabela(linhas, larguras, cab=True, fundo_linhas=None, estilo=peq):
    dados = []
    for i, ln in enumerate(linhas):
        dados.append([c if not isinstance(c, str) else Paragraph(c, peqb if (cab and i == 0) else estilo) for c in ln])
    t = Table(dados, colWidths=larguras, repeatRows=1 if cab else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if cab:
        st.append(("BACKGROUND", (0, 0), (-1, 0), CINZA))
    for linha, cor in (fundo_linhas or {}).items():
        st.append(("BACKGROUND", (0, linha), (-1, linha), cor))
    t.setStyle(TableStyle(st))
    return t


def situacao(cod):
    return {"I": "Implementado", "I*": "Implementado*", "P": "Parcial", "N": "Pendente"}[cod]


COR_SIT = {"I": VERDE, "I*": VERDE, "P": AMARELO, "N": colors.white}

# ---- rodape ---------------------------------------------------------------------------
def rodape(canv, doc):
    canv.saveState()
    w, h = canv._pagesize
    canv.setFont(F, 7.5)
    canv.setFillColor(colors.HexColor("#616e7c"))
    canv.drawString(28, 18, "Conquista — Lab03S01: Modelagem (versão atualizada após a Sprint 2)")
    canv.drawRightString(w - 28, 18, "Pág. %d" % doc.page)
    canv.restoreState()


def capa(canv, doc):
    pass


# ======================================================================================
# conteudo
# ======================================================================================
S = []

# ---- capa ------------------------------------------------------------------------------
S += [Spacer(1, 46 * mm),
      P("Pontifícia Universidade Católica de Minas Gerais", sub),
      P("Curso de Engenharia de Software", sub), Spacer(1, 10 * mm),
      P("Conquista — Sistema de Moeda Estudantil", tit),
      P("Lab03S01: Modelagem (versão atualizada após a Sprint 2)", ParagraphStyle("s2", parent=sub, fontName=FB, fontSize=13)),
      Spacer(1, 12 * mm),
      P("<b>Disciplina:</b> Projeto de Software", sub),
      P("<b>Professora:</b> Milena Menezes Adão", sub), Spacer(1, 8 * mm),
      P("<b>Alunos:</b> Felipe Costa Lisboa, Arthur Martins Candido, Gustavo Leonardi Ribeiro e Sofia Fernandes Ferreira Silva", sub),
      Spacer(1, 8 * mm),
      P("<b>Entregáveis:</b> Diagrama de Casos de Uso, Histórias do Usuário, Diagrama de Classes, Diagrama de Componentes, "
        "evolução da arquitetura e matriz de rastreabilidade", sub),
      Spacer(1, 22 * mm),
      P("Laboratório 3 — Segundo Semestre/2026 · Documento revisado em 26/10/2026", sub),
      PageBreak()]

# ---- 0. sobre ---------------------------------------------------------------------------
S += [H1("Sobre esta versão"),
      P("Este documento atualiza o <i>Lab03S01-modelagem.pdf</i> (Sprint 1) para refletir a arquitetura efetivamente "
        "implementada na Sprint 2, preservando os requisitos da professora, os identificadores originais de casos de uso "
        "(UC) e histórias (US) e a modelagem conceitual do sistema completo. O documento original não foi alterado."),
      P("<b>Base de conferência.</b> O alinhamento entre modelo e código foi verificado por leitura do código-fonte do repositório "
        "(commit <i>5d253b4</i>, ramo <i>master</i>): modelos SQLAlchemy, schemas Pydantic, routers, services, "
        "repositórios, migração Alembic e páginas React. A execução das suítes de teste não faz parte desta revisão."),
      P("<b>Convenção de situação</b> usada em todos os diagramas e tabelas:"),
      tabela([["Situação", "Significado"],
              ["Implementado", "Existe no código da Sprint 2 e atende aos critérios da história/caso de uso."],
              ["Implementado*", "Funcionalidade pronta, mas sem controle de acesso por perfil, pois a autenticação (US01) ainda não existe."],
              ["Parcial", "Parte dos critérios foi atendida; o restante depende da Sprint 3 (em geral, login e senha)."],
              ["Pendente", "Previsto no enunciado e na modelagem; ainda não implementado."]],
             [32 * mm, 140 * mm], fundo_linhas={1: VERDE, 2: VERDE, 3: AMARELO}),
      Spacer(1, 4),
      P("Autenticação, JWT, APScheduler, e-mail, vantagens, transações e resgates continuam <b>planejados</b> e não são "
        "apresentados como entregues em nenhuma parte deste documento.", nota)]

# ---- 1. atores --------------------------------------------------------------------------
S += [H1("1. Atores"),
      tabela([["Ator", "Descrição"],
              ["Aluno", "Se cadastra, recebe moedas, consulta extrato e troca moedas por vantagens"],
              ["Professor", "Pré-cadastrado pela instituição; envia moedas aos alunos e consulta extrato"],
              ["Empresa Parceira", "Se cadastra, cadastra vantagens e confere cupons de resgate"],
              ["Sistema (agendamento e notificações)", "Ator secundário: credita 1.000 moedas por semestre aos professores e dispara e-mails"]],
             [55 * mm, 117 * mm]),
      Spacer(1, 4),
      P("O ator secundário, chamado “Sistema (Scheduler/E-mail)” na Sprint 1, passa a ser identificado como "
        "“Sistema de agendamento e notificações”, sem mudança de responsabilidade.", nota),
      PageBreak()]

# ---- 2. casos de uso --------------------------------------------------------------------
S += [H1("2. Diagrama de Casos de Uso"), DiagramaCasosDeUso(),
      P("Figura 1 — Diagrama de Casos de Uso (situação na Sprint 2)", leg), PageBreak(),
      H2("2.1 Descrição resumida dos casos de uso")]

uc = [
    ["ID", "Caso de uso", "Ator", "Pré-condição", "Fluxo principal", "Pós-condição", "Situação"],
    ["UC01", "Autenticar", "Aluno, Professor, Empresa", "Possuir login e senha", "Informa login/senha → sistema valida → cria sessão conforme perfil", "Usuário autenticado", "Pendente"],
    ["UC02", "Cadastrar aluno", "Aluno", "-", "Informa nome, e-mail, CPF, RG, endereço, curso, escolhe instituição (pré-cadastrada), define login/senha", "Aluno criado com saldo 0", "Parcial (sem login/senha)"],
    ["UC03", "Gerenciar perfil do aluno (CRUD)", "Aluno", "Autenticado", "Visualiza, edita e exclui os próprios dados (CPF não editável; exclusão com confirmação)", "Cadastro atualizado ou removido", "Implementado*"],
    ["UC04", "Cadastrar empresa parceira", "Empresa", "-", "Informa dados da empresa e define login/senha", "Empresa criada", "Parcial (sem login/senha)"],
    ["UC05", "Gerenciar empresa (CRUD)", "Empresa", "Autenticada", "Visualiza, edita e exclui os próprios dados (CNPJ não editável; exclusão com confirmação)", "Cadastro atualizado ou removido", "Implementado*"],
    ["UC06", "Cadastrar vantagem", "Empresa", "Autenticada", "Informa nome, descrição, foto e custo em moedas", "Vantagem disponível para resgate", "Pendente"],
    ["UC07", "Listar vantagens", "Aluno", "Autenticado", "Visualiza vantagens com foto, descrição, custo e empresa", "-", "Pendente"],
    ["UC08", "Enviar moedas", "Professor", "Autenticado; saldo suficiente", "Seleciona aluno, informa valor e motivo (obrigatório) → debita professor, credita aluno, registra transação", "Aluno notificado por e-mail", "Pendente"],
    ["UC09", "Consultar extrato", "Aluno, Professor", "Autenticado", "Exibe saldo atual e histórico de transações (professor: envios; aluno: recebimentos e trocas)", "-", "Pendente"],
    ["UC10", "Trocar moedas", "Aluno", "Autenticado; saldo ≥ custo", "Seleciona vantagem → debita saldo → gera código → registra resgate", "E-mail de cupom ao aluno e e-mail de conferência à empresa, ambos com o código", "Pendente"],
    ["UC11", "Conferir cupom", "Empresa", "Autenticada", "Informa o código apresentado pelo aluno → sistema valida e marca como utilizado", "Resgate marcado como utilizado", "Pendente"],
    ["UC12", "Creditar moedas semestrais", "Sistema", "Início do semestre", "Soma 1.000 moedas ao saldo corrente de cada professor (acumulativo)", "Saldos atualizados", "Pendente"],
    ["UC13", "Enviar e-mail de notificação", "Sistema", "Incluído por UC08 e UC10", "Envia ao aluno o aviso de moedas recebidas (professor, quantidade e motivo) e, no resgate, o cupom ao aluno e a conferência à empresa, ambos com o código", "E-mails enviados", "Pendente"],
]
lin = [uc[0]] + [[r[0], r[1], r[2], r[3], r[4], r[5], r[6]] for r in uc[1:]]
cores = {}
for i, r in enumerate(uc[1:], start=1):
    cores[i] = VERDE if r[6].startswith("Implementado") else (AMARELO if r[6].startswith("Parcial") else colors.white)
S += [tabela(lin, [10 * mm, 22 * mm, 17 * mm, 20 * mm, 52 * mm, 28 * mm, 23 * mm], fundo_linhas=cores),
      Spacer(1, 5),
      P("<b>Fluxos alternativos principais:</b> saldo insuficiente (UC08/UC10) → operação recusada com mensagem; motivo vazio (UC08) "
        "→ bloqueia envio; credenciais inválidas (UC01) → acesso negado; CPF/e-mail já cadastrado (UC02) → erro de validação; "
        "código de cupom inválido ou já usado (UC11) → recusado."),
      P("<b>Observações da revisão.</b> (a) As linhas de UC03, UC05 e UC13 já constavam no diagrama e na matriz de rastreabilidade da "
        "Sprint 1, mas não na tabela de descrições; foram descritas aqui a partir dos requisitos e das histórias US03, US13, US04 e US07. "
        "(b) UC07 recebeu a relação «include» com UC01, pois a Sprint 1 já exigia aluno autenticado como pré-condição. "
        "(c) Nenhum caso de uso foi removido ou acrescentado.", nota),
      PageBreak()]

# ---- 3. historias ----------------------------------------------------------------------
S += [H1("3. Histórias do Usuário"),
      P("Prioridade: <b>A</b> = alta (núcleo / sprints 2–3), <b>M</b> = média, <b>B</b> = baixa. O texto e os critérios de aceite "
        "abaixo são os da Sprint 1, sem alteração.", nota)]

hist = [
    ("Autenticação", [
        ("US01 - Login", "A", "Como aluno, professor ou empresa parceira, quero fazer login com usuário e senha para acessar as funções do meu perfil.",
         "Credenciais válidas redirecionam para a área do perfil correspondente. Credenciais inválidas exibem erro sem informar qual campo está errado. Senhas são armazenadas com hash. Rotas protegidas exigem autenticação e respeitam o perfil."),
    ]),
    ("Aluno", [
        ("US02 - Cadastro de aluno", "A", "Como aluno, quero me cadastrar informando nome, e-mail, CPF, RG, endereço, instituição e curso para participar do sistema de mérito.",
         "instituição escolhida em lista pré-cadastrada; CPF e e-mail únicos; todos os campos obrigatórios validados; saldo inicial 0."),
        ("US03 - Editar/excluir meu cadastro", "A", "Como aluno, quero visualizar, editar e excluir meus dados para mantê-los atualizados.",
         "edição não permite alterar CPF; exclusão exige confirmação."),
        ("US04 - Notificação de moedas recebidas", "A", "Como aluno, quero ser notificado por e-mail ao receber moedas para saber quem me reconheceu e por quê.",
         "e-mail contém professor, quantidade e motivo."),
        ("US05 - Extrato do aluno", "A", "Como aluno, quero consultar meu saldo e histórico (recebimentos e trocas) para acompanhar minhas moedas.",
         "exibe saldo atual; transações ordenadas da mais recente para a mais antiga, com data, tipo, valor e descrição."),
        ("US06 - Listar vantagens", "A", "Como aluno, quero ver as vantagens disponíveis, com foto, descrição e custo, para escolher o que trocar.",
         "mostra empresa, custo em moedas e indica se meu saldo é suficiente."),
        ("US07 - Trocar moedas por vantagem", "A", "Como aluno, quero trocar minhas moedas por uma vantagem para usufruir do benefício na empresa parceira.",
         "bloqueia se saldo &lt; custo; debita o valor; gera código único; envia e-mail de cupom ao aluno e e-mail de conferência à empresa, ambos com o código; operação atômica (transação de banco)."),
    ]),
    ("Professor", [
        ("US08 - Enviar moedas", "A", "Como professor, quero enviar moedas a um aluno da minha instituição, com um motivo, para reconhecer bom desempenho.",
         "exige saldo suficiente; motivo obrigatório; aluno deve pertencer à mesma instituição; debita professor e credita aluno na mesma transação."),
        ("US09 - Extrato do professor", "A", "Como professor, quero consultar meu saldo e os envios realizados para controlar minha distribuição.",
         "mostra saldo e lista de envios com aluno, valor, motivo e data."),
        ("US10 - Crédito semestral", "M", "Como professor, quero receber 1.000 moedas a cada semestre, acumulando o saldo não utilizado, para continuar reconhecendo meus alunos.",
         "crédito executado uma vez por semestre; soma ao saldo corrente; registrado no extrato."),
        ("US11 - Professor pré-cadastrado", "M", "Como instituição parceira, quero enviar a lista de professores (nome, CPF, departamento) para que eles já existam no sistema vinculados à instituição.",
         "professor sempre vinculado a uma instituição; carga inicial via seed/importação."),
    ]),
    ("Empresa parceira", [
        ("US12 - Cadastro de empresa parceira", "A", "Como empresa, quero me cadastrar com login e senha para oferecer vantagens aos alunos.",
         "dados obrigatórios validados; CNPJ/e-mail únicos."),
        ("US13 - Editar/excluir empresa", "A", "Como empresa, quero editar e excluir meus dados para mantê-los corretos.", None),
        ("US14 - Cadastrar vantagem", "A", "Como empresa, quero cadastrar vantagens com descrição, foto e custo em moedas para atrair alunos.",
         "nome, descrição, foto e custo &gt; 0 obrigatórios; vantagem vinculada à empresa logada; empresa pode editar/desativar suas vantagens."),
        ("US15 - Conferir cupom", "M", "Como empresa, quero validar o código apresentado pelo aluno para confirmar a troca presencial.",
         "código válido e não utilizado é marcado como usado; código inválido ou repetido é recusado."),
    ]),
    ("Dados de apoio", [
        ("US16 - Instituições pré-cadastradas", "M", "Como aluno, quero selecionar minha instituição em uma lista para me vincular corretamente.",
         "lista carregada do banco (seed inicial)."),
    ]),
]
for grupo, hs in hist:
    S.append(H2(grupo))
    for titulo, prio, texto, crit in hs:
        bloco = [P("%s <font name='%s' size='8'>(%s)</font>" % (titulo, F, prio), us_t), P(texto, us_b)]
        if crit:
            bloco.append(P("<b>Critérios de aceite:</b> " + crit, us_b))
        S.append(KeepTogether(bloco))

S += [H2("3.1 Acompanhamento da implementação (Sprint 2)"),
      P("Classificação feita critério a critério. Como a autenticação ainda não existe, nenhuma história que exige login e senha "
        "foi marcada como totalmente concluída.", nota)]
acomp = [
    ("US01", "Login", "N", "Sem autenticação; <i>senha_hash</i> existe no modelo, mas é opcional e nunca preenchida."),
    ("US02", "Cadastro de aluno", "P", "Atendidos: dados, endereço, instituição em lista, CPF/e-mail únicos, validação, saldo inicial 0. Pendente: definição de login/senha."),
    ("US03", "Edição e exclusão de aluno", "I*", "Atendidos: CPF imutável e exclusão com confirmação. Sem restrição ao “meu” cadastro (depende de US01)."),
    ("US04", "Notificação por e-mail", "N", "Não há serviço de e-mail."),
    ("US05", "Extrato do aluno", "N", "Não há transações."),
    ("US06", "Listar vantagens", "N", "Entidade Vantagem ainda não existe."),
    ("US07", "Trocar moedas por vantagem", "N", "Sem vantagens, resgates ou cupons."),
    ("US08", "Enviar moedas", "N", "Sem professores nem transações."),
    ("US09", "Extrato do professor", "N", "Sem professores nem transações."),
    ("US10", "Crédito semestral", "N", "APScheduler não adotado."),
    ("US11", "Professor pré-cadastrado", "N", "O seed atual carrega apenas instituições de ensino."),
    ("US12", "Cadastro de empresa", "P", "Atendidos: dados obrigatórios validados, CNPJ/e-mail únicos. Pendente: login e senha."),
    ("US13", "Edição e exclusão de empresa", "I*", "CRUD completo com confirmação e CNPJ imutável; sem restrição à empresa logada (depende de US01)."),
    ("US14", "Cadastrar vantagem", "N", "Vantagem não implementada."),
    ("US15", "Conferir cupom", "N", "Cupom não implementado."),
    ("US16", "Instituições pré-cadastradas", "I", "Endpoint <i>/api/instituicoes</i> lista instituições carregadas do banco pelo seed."),
]
S.append(tabela([["História", "Funcionalidade", "Situação", "Justificativa"]] +
                [[a, b, situacao(c), d] for a, b, c, d in acomp],
                [16 * mm, 40 * mm, 24 * mm, 92 * mm],
                fundo_linhas={i: COR_SIT[r[2]] for i, r in enumerate(acomp, start=1)}))
S += [Spacer(1, 3), P("* Funcionalidade pronta, sem controle de acesso por perfil até a Sprint 3.", nota),
      NextPageTemplate("paisagem"), PageBreak()]

# ---- 4. classes -------------------------------------------------------------------------
S += [H1("4. Diagrama de Classes"), DiagramaClasses(),
      P("Figura 2 — Diagrama de Classes (modelo conceitual completo; situação na Sprint 2 indicada por cor e borda)", leg),
      NextPageTemplate("retrato"), PageBreak(),
      H2("Decisões de modelagem")]
S += [P(t, item) for t in [
    "• " + code("Usuario") + " centraliza e-mail, senha e perfil (herança), atendendo ao requisito de autenticação para os três tipos de ator. "
    "Na Sprint 2 a tabela " + code("usuarios") + " já existe, com " + code("tipo") + " restrito a ALUNO e EMPRESA e " + code("senha_hash") + " opcional.",
    "• " + code("Transacao") + " é abstrata com duas especializações: " + code("TransacaoEnvio") + " (professor → aluno, com motivo obrigatório) e "
    + code("TransacaoResgate") + " (aluno → vantagem, com código de cupom). O extrato é a consulta dessas transações por usuário.",
    "• O vínculo professor–instituição é obrigatório, conforme o enunciado; o vínculo aluno–instituição é obrigatório e já é imposto pelo banco "
    "(chave estrangeira não nula com " + code("ON DELETE RESTRICT") + ").",
    "• O envio só é permitido se " + code("professor.saldo &gt;= valor") + " e " + code("valor &gt; 0") + "; resgate só se " + code("aluno.saldo &gt;= vantagem.custo_moedas") + ".",
    "• <b>Saldo protegido.</b> " + code("saldo") + " é atributo privado. Os schemas de cadastro e edição do aluno não aceitam saldo; o cadastro "
    "cria o saldo com 0 e a alteração ficará restrita às operações de moeda da Sprint 3.",
    "• <b>Unicidade.</b> E-mail único em " + code("Usuario") + ", CPF único em " + code("Aluno") + " e CNPJ único em " + code("EmpresaParceira")
    + ", garantidos por restrição " + code("UNIQUE") + " no banco e por verificação prévia nos services (resposta 409). CPF e CNPJ não são editáveis após o cadastro.",
    "• " + code("Endereco") + " está ligado a " + code("Usuario") + " (composição 1–1), e não mais diretamente ao aluno, como na Sprint 1.",
    "• Os métodos do diagrama são conceituais. Na Sprint 2 as classes persistidas são entidades sem comportamento; as regras ficam nos Services.",
]]
S += [H2("Modelo conceitual × entidades persistidas na Sprint 2"),
      tabela([["Classe conceitual", "Situação", "Persistência na Sprint 2", "Diferenças em relação à Sprint 1"],
              ["Usuario", "Parcial", "Tabela usuarios: id, nome, email (único), tipo, senha_hash (opcional), criado_em, atualizado_em",
               "nome passou para Usuario (antes em Aluno/Professor); login ainda não existe (e-mail identifica o usuário); tipo aceita ALUNO e EMPRESA"],
              ["Aluno", "Implementada", "Tabela alunos (PK = usuario_id): cpf, rg, curso, instituicao_id, saldo Numeric(14,2)",
               "saldo conceitual é inteiro; no banco é decimal com 2 casas — a definir na Sprint 3"],
              ["EmpresaParceira", "Implementada", "Tabela empresas_parceiras (PK = usuario_id): cnpj, telefone",
               "nome_fantasia corresponde a Usuario.nome; telefone foi acrescentado"],
              ["InstituicaoEnsino", "Implementada", "Tabela instituicoes_ensino: id, nome (único), sigla (única)", "sigla acrescentada"],
              ["Endereco", "Implementada", "Tabela enderecos: usuario_id (único), logradouro, numero, complemento, bairro, cidade, estado, cep", "associado a Usuario"],
              ["Perfil", "Parcial", "Restrição CHECK em usuarios.tipo", "PROFESSOR ainda não aceito"],
              ["Professor, Vantagem, Transacao, TransacaoEnvio, TransacaoResgate, StatusCupom", "Prevista", "Não persistidas", "Sem alteração conceitual"]],
             [34 * mm, 21 * mm, 62 * mm, 55 * mm],
             fundo_linhas={1: AMARELO, 2: VERDE, 3: VERDE, 4: VERDE, 5: VERDE, 6: AMARELO}),
      NextPageTemplate("paisagem"), PageBreak()]

# ---- 5. componentes ---------------------------------------------------------------------
S += [H1("5. Diagrama de Componentes (arquitetura MVC)"), DiagramaComponentes(),
      P("Figura 3 — Diagrama de Componentes (componentes implementados em verde; previstos com borda tracejada)", leg),
      NextPageTemplate("retrato"), PageBreak()]

S += [H1("6. Descrição da arquitetura"),
      P("<b>Stack implementada na Sprint 2.</b> Front-end: React, TypeScript, Vite, Tailwind CSS, Axios, React Router, React Hook Form, Zod e "
        "Lucide React. Back-end: Python, FastAPI, Pydantic, SQLAlchemy 2, Alembic e Uvicorn. Persistência: PostgreSQL hospedado no Neon, "
        "com padrão Repository sobre SQLAlchemy e migrações Alembic."),
      P("<b>Fluxo de uma requisição:</b> React → Axios (HTTP/JSON, interface API REST em /api) → Routers FastAPI → Services → Repositories → "
        "SQLAlchemy → PostgreSQL. A aplicação é organizada em camadas, com front-end e back-end independentes, de modo compatível com o MVC."),
      P("<b>Execução:</b> " + code("uvicorn app.main:app --reload --port 8000") + " (API) e " + code("npm run dev") + " (cliente, porta 5173)."),
      tabela([["Componente", "Responsabilidade", "Situação"],
              ["View — React + TypeScript", "Telas de cadastro, listagem, busca, consulta e edição de alunos e empresas; dashboard; navegação (React Router); estilo (Tailwind CSS)", "Implementado"],
              ["Formulários — React Hook Form + Zod", "Validação no cliente de campos obrigatórios, CPF, CNPJ e e-mail", "Implementado"],
              ["Serviços HTTP — Axios", "alunoService, empresaService e instituicaoService; consomem a API REST", "Implementado"],
              ["Controllers — Routers FastAPI", "Entrada HTTP em " + code("/api/alunos") + ", " + code("/api/empresas") + ", " + code("/api/instituicoes") + "; injeção da sessão de banco; códigos de resposta", "Implementado"],
              ["Schemas — Pydantic", "Validação e serialização de entrada e saída (CPF, CNPJ, e-mail, CEP, tamanhos)", "Implementado"],
              ["Services", "AlunoService, EmpresaService e InstituicaoService: regras de negócio, unicidade e controle de transação (rollback e erro 409/404)", "Implementado"],
              ["Repository", "UsuarioRepository (sobre BaseRepository): consultas de alunos, empresas, instituições e unicidade de e-mail", "Implementado"],
              ["Model — SQLAlchemy", "Entidades Usuario, Aluno, EmpresaParceira, Endereco e InstituicaoEnsino, com restrições e chaves estrangeiras", "Implementado"],
              ["Alembic", "Migração " + code("20261026_0001_sprint2") + " cria o schema; " + code("python -m app.database.seed") + " carrega as instituições", "Implementado"],
              ["PostgreSQL (Neon)", "Banco da aplicação; SQLite isolado apenas nos testes automatizados", "Implementado"],
              ["Segurança (OAuth2/JWT, bcrypt, perfis)", "Autenticação e controle de acesso por perfil (US01)", "Previsto"],
              ["AuthRouter, ProfessorRouter, Extrato/Vantagem", "Novos controllers para login, professores, extrato, vantagens e cupons", "Previsto"],
              ["MoedaService, CupomService, AuthService", "Envio e resgate de moedas, geração de cupom, autenticação", "Previsto"],
              ["CreditoSemestralJob (APScheduler)", "Crédito semestral de 1.000 moedas (UC12)", "Previsto"],
              ["Serviço de e-mail (SMTP)", "Notificações de moedas, cupom e conferência (UC13)", "Previsto"],
              ["Armazenamento de fotos", "Foto das vantagens (UC06)", "Previsto"]],
             [46 * mm, 100 * mm, 26 * mm],
             fundo_linhas={i: (VERDE if i <= 10 else colors.white) for i in range(1, 17)}),
      Spacer(1, 4),
      P("<b>Mapeamento MVC → implementação.</b> Model = entidades SQLAlchemy + Services + Repositories; View = cliente React; "
        "Controller = Routers FastAPI. Não são utilizados templates Jinja2. Pydantic (servidor) e Zod (cliente) validam as duas fronteiras.", nota),
      P("<b>Segurança na Sprint 2.</b> Os CRUDs não têm autenticação; portanto a API não deve ser publicada antes da Sprint 3. "
        "Conflitos de integridade geram rollback e resposta 409 sem detalhes internos, e o CORS aceita apenas origens configuradas.", nota)]

# ---- 7. evolucao ------------------------------------------------------------------------
S += [H1("7. Evolução da Arquitetura — Sprint 1 para Sprint 2")]
evo = [
    ("Arquitetura inicialmente proposta",
     "A Sprint 1 propôs uma aplicação MVC monolítica em Python + FastAPI: View com templates Jinja2, Controllers como routers FastAPI, Services, "
     "Repositories (DAO) com SQLAlchemy/Alembic, PostgreSQL, APScheduler, OAuth2/JWT e SMTP."),
    ("Substituição de Jinja2 por React + TypeScript",
     "A View deixou de ser renderizada no servidor e passou a ser um cliente React com TypeScript, construído com Vite, Tailwind CSS, React Router, "
     "React Hook Form, Zod e Lucide React. O papel de View do MVC foi preservado."),
    ("Separação entre front-end e back-end",
     "Passam a existir dois projetos independentes (" + code("frontend/") + " e " + code("backend/") + "), executados e testados separadamente. "
     "O back-end não serve mais HTML."),
    ("Comunicação por API REST",
     "O cliente usa Axios para consumir uma API JSON sob " + code("/api") + ". Pydantic valida a entrada e a saída no servidor; o CORS libera apenas as origens configuradas."),
    ("Adoção de SQLAlchemy e Repository",
     "A persistência segue o plano da Sprint 1: SQLAlchemy 2 como ORM e repositórios isolando as consultas. Na Sprint 2 existe um único repositório concreto "
     "(UsuarioRepository, sobre BaseRepository), suficiente para os dois CRUDs; os demais virão com as novas entidades."),
    ("Uso de PostgreSQL no Neon",
     "O banco é um PostgreSQL gerenciado no Neon, acessado com psycopg 3 e " + code("sslmode=require") + ". Os testes usam SQLite isolado, sem tocar a instância Neon."),
    ("Migrações com Alembic",
     "O schema é versionado pela migração " + code("20261026_0001_sprint2") + ". Um seed idempotente carrega as instituições pré-cadastradas (PUC Minas, UFMG, CEFET-MG)."),
    ("Funcionalidades entregues na Sprint 2",
     "Dashboard com indicadores vindos da API; CRUD de alunos e de empresas parceiras com busca, validação de CPF, CNPJ, e-mail e campos obrigatórios; "
     "unicidade de CPF, CNPJ e e-mail; CPF e CNPJ imutáveis; saldo inicial 0 protegido; confirmação antes de excluir; seleção de instituições pré-cadastradas; "
     "tratamento de carregamento, erros e listas vazias."),
    ("Componentes previstos para as próximas etapas",
     "Autenticação (OAuth2/JWT, hash de senha, perfis), professores pré-cadastrados, envio de moedas, extrato, vantagens com foto, resgate com cupom, "
     "serviço de e-mail (SMTP) e crédito semestral com APScheduler. Nenhum desses itens está implementado."),
]
for i, (t, d) in enumerate(evo, start=1):
    S.append(KeepTogether([P("<b>%d. %s.</b> %s" % (i, t, d), base)]))
S += [NextPageTemplate("paisagem"), PageBreak()]

# ---- 8. rastreabilidade -----------------------------------------------------------------
S += [H1("8. Rastreabilidade (requisito → caso de uso → história → classe → componente)")]
rast = [
    ["Requisito do enunciado", "Caso de uso", "História", "Classes principais", "Componentes", "Situação"],
    ["Cadastro de aluno", "UC02, UC03", "US02, US03", "Aluno, Usuario, Endereco, InstituicaoEnsino", "React (páginas/formulários), Routers, Schemas, AlunoService, UsuarioRepository, SQLAlchemy", "UC02/US02 parcial; UC03/US03 implementado*"],
    ["Instituições pré-cadastradas para seleção", "UC02", "US16", "InstituicaoEnsino", "InstituicaoService, UsuarioRepository, Alembic (seed), PostgreSQL", "Implementado"],
    ["Professores pré-cadastrados com instituição", "-", "US11", "Professor, InstituicaoEnsino", "ProfessorRouter, Repository de Professor, seed", "Pendente"],
    ["1.000 moedas/semestre acumuláveis", "UC12", "US10", "Professor", "CreditoSemestralJob (APScheduler)", "Pendente"],
    ["Envio de moedas com motivo", "UC08", "US08", "TransacaoEnvio, Professor, Aluno", "MoedaService, ProfessorRouter", "Pendente"],
    ["E-mail ao aluno ao receber moedas", "UC13", "US04", "TransacaoEnvio", "Serviço de e-mail (SMTP)", "Pendente"],
    ["Extrato (aluno e professor)", "UC09", "US05, US09", "Transacao", "Extrato/VantagemRouter, Repository de Transacao", "Pendente"],
    ["Cadastro de empresa", "UC04, UC05", "US12, US13", "EmpresaParceira, Usuario, Endereco", "React, Routers, Schemas, EmpresaService, UsuarioRepository, SQLAlchemy", "UC04/US12 parcial; UC05/US13 implementado*"],
    ["Cadastro e listagem de vantagens", "UC06, UC07", "US06, US14", "Vantagem, EmpresaParceira", "Extrato/VantagemRouter, Armazenamento de fotos", "Pendente"],
    ["Troca de moedas + e-mails com código", "UC10, UC13", "US07", "TransacaoResgate, Vantagem, Aluno", "MoedaService, CupomService, Serviço de e-mail", "Pendente"],
    ["Conferência pelo parceiro", "UC11", "US15", "TransacaoResgate", "CupomService, Extrato/VantagemRouter", "Pendente"],
    ["Login e senha para todos", "UC01", "US01", "Usuario, Perfil", "AuthRouter, AuthService, Segurança (OAuth2/JWT, bcrypt)", "Pendente"],
]
fundos = {1: AMARELO, 2: VERDE, 8: AMARELO}
S += [tabela(rast, [50 * mm, 22 * mm, 22 * mm, 55 * mm, 80 * mm, 45 * mm][:6], fundo_linhas=fundos),
      Spacer(1, 4),
      P("Os identificadores de requisitos, casos de uso e histórias são os da Sprint 1. Foram acrescentadas duas linhas — instituições "
        "pré-cadastradas (US16) e listagem de vantagens (UC07/US06) — que já existiam como UC/US, mas não constavam na matriz original.", nota),
      NextPageTemplate("retrato"), PageBreak()]

# ---- 9. conclusao -----------------------------------------------------------------------
S += [H1("9. Conclusão — alinhamento entre modelagem e implementação"),
      P("A modelagem da Sprint 1 permanece válida como visão conceitual do sistema completo. A revisão alterou a camada de apresentação "
        "(Jinja2 → React + TypeScript), tornou explícita a separação entre front-end e back-end e registrou a pilha realmente adotada, "
        "mantendo o padrão em camadas e a aderência ao MVC."),
      P("<b>Alinhado.</b> Os cinco elementos persistidos (Usuario, Aluno, EmpresaParceira, InstituicaoEnsino e Endereco), seus relacionamentos, a herança "
        "de Usuario, a obrigatoriedade da instituição para o aluno, as regras de unicidade de e-mail, CPF e CNPJ e a proteção do saldo correspondem ao código."),
      P("<b>Divergências registradas (a decidir na Sprint 3).</b> (1) O login ainda não existe; o e-mail é o único identificador. (2) O saldo é inteiro no modelo conceitual "
        "e decimal com 2 casas no banco. (3) O perfil PROFESSOR ainda não é aceito pela restrição de " + code("usuarios.tipo") + ". "
        "(4) Endereço ficou associado a Usuario, e não a Aluno."),
      P("<b>Pendente para a Sprint 3.</b> Autenticação e controle de acesso (US01), professores, transações de envio e resgate, vantagens, cupons, "
        "e-mails e crédito semestral. Esses itens permanecem na modelagem conceitual, mas não estão implementados."),
      P("<b>Ressalva.</b> O alinhamento foi conferido por leitura do código-fonte no commit 5d253b4; deve ser reconferido a cada nova migração.", nota)]


# ---- documento ---------------------------------------------------------------------------
def montar():
    doc = BaseDocTemplate(SAIDA, pagesize=A4, title="Conquista — Lab03S01: Modelagem (atualizada)",
                          author="Felipe Costa Lisboa, Arthur Martins Candido, Gustavo Leonardi Ribeiro, Sofia Fernandes Ferreira Silva",
                          subject="Projeto de Software — PUC Minas")
    pw, ph = A4
    retrato = PageTemplate("retrato", [Frame(19 * mm, 18 * mm, pw - 38 * mm, ph - 33 * mm, id="r", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                           onPage=rodape, pagesize=A4)
    lw, lh = landscape(A4)
    paisagem = PageTemplate("paisagem", [Frame(28, 26, lw - 56, lh - 46, id="p", leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
                            onPage=rodape, pagesize=landscape(A4))
    doc.addPageTemplates([retrato, paisagem])
    doc.build(S)


if __name__ == "__main__":
    montar()
    print("ok", SAIDA)
