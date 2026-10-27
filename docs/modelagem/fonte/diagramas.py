"""Diagramas UML (caso de uso, classes e componentes) desenhados como vetores."""
import math

from reportlab.lib import colors

from desenho import (F, FB, FI, FM, GRID, INK, LAYER_FILL, PART_LINE, IMPL_LINE, PLAN_LINE,
                     Diagrama, STATUS_STYLE)


# ======================================================================================
# Diagrama de classes
# ======================================================================================
class DiagramaClasses(Diagrama):
    def __init__(self):
        super().__init__(780, 508, 0.94)

    def desenhar(self):
        # ---- classes -------------------------------------------------------------
        defs = {
            "Perfil": dict(x=125, y=20, w=105, est="enumeration", status="parcial",
                           atrib=["ALUNO", "PROFESSOR", "EMPRESA"], met=[]),
            "Usuario": dict(x=300, y=0, w=170, est="abstract", status="parcial",
                            atrib=["- id: int", "- nome: str", "- email: str {unique}", "- login: str",
                                   "- senha_hash: str", "- perfil: Perfil"],
                            met=["+ autenticar(senha): bool"]),
            "Endereco": dict(x=560, y=0, w=150, est=None, status="impl",
                             atrib=["- id: int", "- logradouro: str", "- numero: str", "- complemento: str",
                                    "- bairro: str", "- cidade: str", "- estado: str", "- cep: str"], met=[]),
            "Professor": dict(x=30, y=150, w=190, est=None, status="plan",
                              atrib=["- cpf: str", "- departamento: str", "- saldo: int"],
                              met=["+ enviar_moedas(aluno, valor, motivo)", "+ creditar_semestre(valor)",
                                   "+ consultar_extrato(): list[Transacao]"]),
            "Aluno": dict(x=300, y=150, w=170, est=None, status="impl",
                          atrib=["- cpf: str {unique}", "- rg: str", "- curso: str", "- saldo: Decimal"],
                          met=["+ receber_moedas(valor)", "+ debitar(valor)", "+ consultar_extrato(): list[Transacao]"]),
            "EmpresaParceira": dict(x=560, y=150, w=190, est=None, status="impl",
                                    atrib=["- cnpj: str {unique}", "- telefone: str"],
                                    met=["+ cadastrar_vantagem(v)", "+ conferir_cupom(codigo): bool"]),
            "InstituicaoEnsino": dict(x=140, y=285, w=140, est=None, status="impl",
                                      atrib=["- id: int", "- nome: str {unique}", "- sigla: str {unique}"], met=[]),
            "Vantagem": dict(x=560, y=255, w=190, est=None, status="plan",
                             atrib=["- id: int", "- nome: str", "- descricao: str", "- foto_url: str",
                                    "- custo_moedas: int", "- ativa: bool"], met=[]),
            "TransacaoEnvio": dict(x=30, y=375, w=150, est=None, status="plan", atrib=["- motivo: str"], met=[]),
            "Transacao": dict(x=310, y=392, w=150, est="abstract", status="plan",
                              atrib=["- id: int", "- data: datetime", "- valor: int"], met=["+ descricao(): str"]),
            "TransacaoResgate": dict(x=560, y=392, w=190, est=None, status="plan",
                                     atrib=["- codigo_cupom: str", "- status: StatusCupom"], met=[]),
            "StatusCupom": dict(x=468, y=442, w=90, est="enumeration", status="plan",
                                atrib=["EMITIDO", "UTILIZADO"], met=[]),
        }
        box = {}
        for nome, d in defs.items():
            h = self.classe(d["x"], d["y"], d["w"], nome, d["atrib"], d["met"], d["est"], d["status"])
            box[nome] = (d["x"], d["y"], d["w"], h)

        def L(n): return box[n][0]
        def R(n): return box[n][0] + box[n][2]
        def T(n): return box[n][1]
        def B(n): return box[n][1] + box[n][3]
        def CX(n): return box[n][0] + box[n][2] / 2
        def CY(n): return box[n][1] + box[n][3] / 2

        # ---- Usuario -> Perfil (associacao dirigida) --------------------------------
        y = 60
        self.linha([(L("Usuario"), y), (R("Perfil"), y)])
        self.seta_aberta((R("Perfil"), y), (L("Usuario"), y))
        self.rotulo((L("Usuario") + R("Perfil")) / 2, y - 3, "perfil", alinh="c")
        self.texto(L("Usuario") - 4, y + 9, "1", F, 6.2, INK, "r")

        # ---- Usuario <>-- Endereco (composicao 1..1) ------------------------------
        y = 60
        self.linha([(R("Usuario"), y), (L("Endereco"), y)])
        self.losango((R("Usuario"), y), (L("Endereco"), y), cheio=True)
        self.rotulo((R("Usuario") + L("Endereco")) / 2, y - 3, "possui", alinh="c")
        self.texto(R("Usuario") + 12, y + 9, "1", F, 6.2)
        self.texto(L("Endereco") - 3, y + 9, "1", F, 6.2, INK, "r")

        # ---- generalizacao Usuario <|-- Professor / Aluno / EmpresaParceira ----------
        ub = B("Usuario")
        barra = (ub + T("Aluno")) / 2 + 2
        self.triangulo_vazio((CX("Usuario"), ub), (CX("Usuario"), barra))
        self.linha([(CX("Usuario"), ub + 8), (CX("Usuario"), barra)])
        self.linha([(CX("Professor"), barra), (CX("EmpresaParceira"), barra)])
        for n in ("Professor", "Aluno", "EmpresaParceira"):
            self.linha([(CX(n), barra), (CX(n), T(n))])

        # ---- Professor/Aluno -> InstituicaoEnsino ---------------------------------------
        yi = CY("InstituicaoEnsino")
        px = CX("Professor") - 40
        self.linha([(px, B("Professor")), (px, yi), (L("InstituicaoEnsino"), yi)])
        self.seta_aberta((L("InstituicaoEnsino"), yi), (px, yi))
        self.rotulo(px + 3, yi - 4, "pertence a", alinh="l")
        self.texto(px - 3, B("Professor") + 9, "*", F, 6.5, INK, "r")
        self.texto(L("InstituicaoEnsino") - 4, yi + 9, "1", F, 6.5, INK, "r")

        ax = L("Aluno") + 22
        yi2 = yi + 10
        self.linha([(ax, B("Aluno")), (ax, yi2), (R("InstituicaoEnsino"), yi2)])
        self.seta_aberta((R("InstituicaoEnsino"), yi2), (ax, yi2))
        self.rotulo((ax + R("InstituicaoEnsino")) / 2, yi2 + 9, "estuda em", alinh="c")
        self.texto(ax + 4, B("Aluno") + 9, "*", F, 6.5)
        self.texto(R("InstituicaoEnsino") + 4, yi2 - 3, "1", F, 6.5)

        # ---- Empresa <>-- Vantagem (agregacao 1..*) -------------------------------------
        vx = CX("EmpresaParceira")
        self.linha([(vx, B("EmpresaParceira")), (vx, T("Vantagem"))])
        self.losango((vx, B("EmpresaParceira")), (vx, T("Vantagem")), cheio=False)
        self.rotulo(vx + 20, (B("EmpresaParceira") + T("Vantagem")) / 2 + 3, "oferece", alinh="l")
        self.texto(vx + 5, B("EmpresaParceira") + 18, "1", F, 6.5)
        self.texto(vx + 5, T("Vantagem") - 3, "*", F, 6.5)

        # ---- TransacaoEnvio -> Professor (remetente) -------------------------------------
        yl = CY("TransacaoEnvio") - 5
        self.linha([(L("TransacaoEnvio"), yl), (10, yl), (10, CY("Professor")), (L("Professor"), CY("Professor"))])
        self.seta_aberta((L("Professor"), CY("Professor")), (10, CY("Professor")))
        self.rotulo(12, 300, "remetente", alinh="l")
        self.texto(14, CY("Professor") - 4, "1", F, 6.5)
        self.texto(L("TransacaoEnvio") - 3, yl - 3, "*", F, 6.5, INK, "r")

        # ---- TransacaoEnvio -> Aluno (destinatario) --------------------------------------
        xd = CX("Aluno") + 55
        ye = CY("TransacaoEnvio") + 5
        self.linha([(R("TransacaoEnvio"), ye), (xd, ye), (xd, B("Aluno"))])
        self.seta_aberta((xd, B("Aluno")), (xd, ye))
        self.rotulo(xd + 3, 345, "destinatário", alinh="l")
        self.texto(xd + 4, B("Aluno") + 10, "1", F, 6.5)
        self.texto(R("TransacaoEnvio") + 4, ye - 3, "*", F, 6.5)

        # ---- TransacaoResgate -> Aluno (realizado por) -----------------------------------
        xr = 515
        yr = T("TransacaoResgate") + 9
        ya = CY("Aluno")
        self.linha([(L("TransacaoResgate"), yr), (xr, yr), (xr, ya), (R("Aluno"), ya)])
        self.seta_aberta((R("Aluno"), ya), (xr, ya))
        self.rotulo(xr + 3, 300, "realizado por", alinh="l")
        self.texto(R("Aluno") + 4, ya - 3, "1", F, 6.5)
        self.texto(L("TransacaoResgate") - 4, yr - 3, "*", F, 6.5, INK, "r")

        # ---- TransacaoResgate -> Vantagem (resgata) --------------------------------------
        self.linha([(vx, T("TransacaoResgate")), (vx, B("Vantagem"))])
        self.seta_aberta((vx, B("Vantagem")), (vx, T("TransacaoResgate")))
        self.rotulo(vx + 4, (B("Vantagem") + T("TransacaoResgate")) / 2 + 3, "resgata", alinh="l")
        self.texto(vx + 5, B("Vantagem") + 11, "1", F, 6.5)
        self.texto(vx + 5, T("TransacaoResgate") - 3, "*", F, 6.5)

        # ---- generalizacao Transacao <|-- Envio / Resgate -------------------------------------
        yb = T("Transacao") + 27
        self.linha([(R("Transacao") + 8, yb), (L("TransacaoResgate"), yb)])
        self.triangulo_vazio((R("Transacao"), yb), (R("Transacao") + 20, yb))
        yb2 = B("Transacao") - 12
        self.linha([(CX("TransacaoEnvio"), B("TransacaoEnvio")), (CX("TransacaoEnvio"), yb2 + 0),
                    (L("Transacao") - 8, yb2)])
        self.triangulo_vazio((L("Transacao"), yb2), (L("Transacao") - 20, yb2))

        # ---- TransacaoResgate -> StatusCupom (tipo do atributo) ------------------------------
        xs = R("TransacaoResgate") - 40
        ys = CY("StatusCupom")
        self.linha([(xs, B("TransacaoResgate")), (xs, ys), (R("StatusCupom"), ys)], tracejado=True)
        self.seta_aberta((R("StatusCupom"), ys), (xs, ys), 4)

        # ---- legenda ------------------------------------------------------------------------
        y0 = 494
        x = self.legenda(0, y0, [("impl", "Implementada na Sprint 2 (persistida)"),
                                 ("parcial", "Parcial (atributos/papéis pendentes)"),
                                 ("plan", "Prevista (Sprint 3)")])
        self.texto(x, y0 + 6.3, "Métodos são conceituais: na Sprint 2 as regras ficam nos Services.", FI, 6.4)


# ======================================================================================
# Diagrama de casos de uso
# ======================================================================================
class DiagramaCasosDeUso(Diagrama):
    def __init__(self):
        super().__init__(495, 600, 0.96)

    @staticmethod
    def borda(el, alvo):
        """Ponto da elipse (cx, cy, rx, ry) na direcao do ponto alvo."""
        cx, cy, rx, ry = el
        dx, dy = (alvo[0] - cx) / rx, (alvo[1] - cy) / ry
        n = (dx * dx + dy * dy) ** 0.5 or 1
        return (cx + rx * dx / n, cy + ry * dy / n)

    def desenhar(self):
        bx, by, bw, bh = 96, 6, 399, 566
        self.retangulo(bx, by, bw, bh, None, raio=6, linha=GRID, preench=None, larg=1)
        self.texto(bx + bw / 2, by + 11, "Sistema de Moeda Estudantil", FB, 7.5, INK, "c")

        ax = 200
        casos = [
            ("UC12", "UC12 Creditar moedas semestrais"), ("UC02", "UC02 Cadastrar aluno"),
            ("UC03", "UC03 Gerenciar perfil do aluno (CRUD)"), ("UC07", "UC07 Listar vantagens"),
            ("UC10", "UC10 Trocar moedas por vantagem"), ("UC09", "UC09 Consultar extrato"),
            ("UC08", "UC08 Enviar moedas"), ("UC04", "UC04 Cadastrar empresa parceira"),
            ("UC05", "UC05 Gerenciar empresa (CRUD)"), ("UC06", "UC06 Cadastrar vantagem"),
            ("UC11", "UC11 Conferir cupom"),
        ]
        status = {"UC02": "parcial", "UC03": "parcial", "UC04": "parcial", "UC05": "parcial"}
        y0, dy = 60, 47
        pos = {}
        for i, (uc, rot) in enumerate(casos):
            cy = y0 + i * dy
            pos[uc] = (ax, cy, 90, 14)
            self.elipse(ax, cy, 90, 14, status.get(uc, "plan"))
            self.texto(ax, cy + 2.5, rot, F, 6.6, INK, "c")

        bxc = 428
        for uc, rot, cy, rxx, ryy in (("UC13", "UC13 Enviar e-mail de notificação", y0 + 5.5 * dy, 60, 15),
                                      ("UC01", "UC01 Autenticar", y0 + 8.5 * dy, 52, 48)):
            pos[uc] = (bxc, cy, rxx, ryy)
            self.elipse(bxc, cy, rxx, ryy, "plan")
            if uc == "UC13":
                self.texto(bxc, cy - 1, "UC13 Enviar e-mail", F, 6.6, INK, "c")
                self.texto(bxc, cy + 7, "de notificação", F, 6.6, INK, "c")
            else:
                self.texto(bxc, cy + 2.5, rot, F, 6.6, INK, "c")

        # atores
        ys = {k: pos[k][1] for k in pos}
        coords = {
            "Sistema": (34, ys["UC12"] - 22, "Sistema\n(agendamento e\nnotificações)"),
            "Aluno": (34, (ys["UC02"] + ys["UC10"]) / 2 - 20, "Aluno"),
            "Professor": (34, (ys["UC09"] + ys["UC08"]) / 2 - 20, "Professor"),
            "Empresa": (34, (ys["UC04"] + ys["UC11"]) / 2 - 26, "Empresa\nParceira"),
        }
        centro = {}
        for k, (cx, y, nome) in coords.items():
            self.ator(cx, y, nome, "ator")
            centro[k] = (cx + 7, y + 18)

        assoc = [("Sistema", "UC12"), ("Aluno", "UC02"), ("Aluno", "UC03"), ("Aluno", "UC07"),
                 ("Aluno", "UC10"), ("Aluno", "UC09"), ("Professor", "UC09"), ("Professor", "UC08"),
                 ("Empresa", "UC04"), ("Empresa", "UC05"), ("Empresa", "UC06"), ("Empresa", "UC11")]
        for a_, uc in assoc:
            self.linha([centro[a_], self.borda(pos[uc], centro[a_])], larg=0.7)

        # Sistema -> UC13 (ator secundario): contorna por cima dos casos de uso
        sx, sy = centro["Sistema"]
        topo = (bxc, pos["UC13"][1] - pos["UC13"][3])
        ytopo = by + 26
        self.linha([(sx + 3, sy - 6), (sx + 3, ytopo), (bxc, ytopo), topo], larg=0.7)

        # include: tracejado, seta no caso de uso incluido
        def incl(src, dst):
            sx_, sy_, srx, _ = pos[src]
            p_src = (sx_ + srx, sy_)
            p_mid = (sx_ + srx + 18, sy_)
            p_dst = self.borda(pos[dst], p_mid)
            self.linha([p_src, p_mid, p_dst], tracejado=True, larg=0.7)
            self.seta_aberta(p_dst, p_mid, tam=5)

        for s_ in ("UC03", "UC07", "UC09", "UC08", "UC10", "UC05", "UC06", "UC11"):
            incl(s_, "UC01")
        for s_ in ("UC10", "UC08"):
            incl(s_, "UC13")
        self.rotulo(bxc - 4, pos["UC13"][1] + 28, "«include»", alinh="c")

        self.legenda(0, 586, [("parcial", "Parcial na Sprint 2 (sem login/senha)"), ("plan", "Prevista (Sprint 3)")])
        self.texto(300, 592.3, "Seta tracejada = «include»", FI, 6.4)


# ======================================================================================
# Diagrama de componentes
# ======================================================================================
class DiagramaComponentes(Diagrama):
    def __init__(self):
        super().__init__(780, 500, 0.94)

    def componente(self, x, y, w, h, titulo, linhas=(), status="plan", est="component"):
        self.retangulo(x, y, w, h, status, raio=2)
        # simbolo de componente UML (dois retangulos pequenos)
        fill, line, _ = STATUS_STYLE[status]
        self.retangulo(x - 4, y + 6, 8, 4, None, preench=fill, linha=line)
        self.retangulo(x - 4, y + 13, 8, 4, None, preench=fill, linha=line)
        self.texto(x + w / 2 + 2, y + 10, "«%s»" % est, F, 5.6, INK, "c")
        self.texto(x + w / 2 + 2, y + 19, titulo, FB, 6.8, INK, "c")
        for i, s in enumerate(linhas):
            self.texto(x + w / 2 + 2, y + 28 + i * 8, s, F, 6, INK, "c")

    def camada(self, x, y, w, h, titulo):
        self.retangulo(x, y, w, h, None, raio=5, linha=GRID, preench=LAYER_FILL, larg=0.9)
        if x == 0:
            self.texto(x + w - 8, y + 10, titulo, FB, 7.2, INK, "r")
        else:
            self.texto(x + 6, y + 10, titulo, FB, 7.2, INK)

    def desenhar(self):
        W = 780
        # -------- camadas -----------------------------------------------------------
        self.camada(0, 0, 570, 78, "Cliente — View (navegador)")
        self.camada(0, 110, 570, 112, "Controller — FastAPI (Uvicorn)")
        self.camada(0, 256, 570, 92, "Model — Services (regras de negócio)")
        self.camada(0, 372, 570, 78, "Model — Persistência")
        self.camada(596, 372, 184, 78, "Banco de dados")
        self.camada(596, 110, 184, 238, "Transversais / Infraestrutura")

        # View
        self.componente(14, 22, 170, 46, "Camada de serviços HTTP", ["Axios: alunoService,", "empresaService, instituicaoService"], "impl")
        self.componente(210, 22, 170, 46, "Páginas e Formulários", ["React Hook Form + Zod", "Lucide React"], "impl")
        self.componente(406, 22, 150, 46, "React + TypeScript", ["Vite · Tailwind CSS", "React Router"], "impl")
        self.linha([(210, 45), (184, 45)])
        self.seta_aberta((184, 45), (210, 45), 4)
        self.linha([(406, 45), (380, 45)])
        self.seta_aberta((380, 45), (406, 45), 4)

        # Interface REST: soquete (requerida, no cliente) e bola (provida, pelos Routers)
        ix, iy = 99, 94
        c = self.c
        self.linha([(ix, 68), (ix, iy - 8)])
        pts = [(ix + 8 * math.cos(math.pi * k / 24), iy - 8 * math.sin(math.pi * k / 24)) for k in range(25)]
        self.linha(pts)
        self.linha([(ix, iy + 4.5), (ix, 128)])
        c.setStrokeColor(INK)
        c.setFillColor(colors.white)
        c.setLineWidth(0.8)
        c.circle(ix, iy, 4.5, stroke=1, fill=1)
        self.texto(ix + 14, iy - 2, "«interface» API REST /api", F, 6.2, INK)
        self.texto(ix + 14, iy + 6, "HTTP/JSON", F, 6.2, INK)

        # Controller
        self.componente(14, 128, 170, 44, "Routers FastAPI", ["api.py: /alunos, /empresas,", "/instituicoes, /health"], "impl")
        self.componente(206, 128, 150, 44, "Schemas Pydantic", ["validação de entrada/saída", "CPF, CNPJ, e-mail, CEP"], "impl")
        self.componente(378, 128, 178, 44, "Tratamento de erros", ["404/409/422 sem expor", "detalhes internos; CORS"], "impl")
        self.componente(206, 176, 110, 38, "AuthRouter", ["login, JWT"], "plan")
        self.componente(324, 176, 110, 38, "ProfessorRouter", ["professores, envio"], "plan")
        self.componente(442, 176, 114, 38, "Extrato/Vantagem", ["extrato, vantagens, cupons"], "plan")
        self.linha([(206, 150), (184, 150)])
        self.seta_aberta((184, 150), (206, 150), 4)

        # Services
        self.componente(14, 274, 190, 66, "Services (crud.py)", ["AlunoService · EmpresaService", "InstituicaoService", "regras, unicidade e transações"], "impl")
        self.componente(222, 274, 100, 66, "AuthService", ["JWT/OAuth2, bcrypt"], "plan")
        self.componente(332, 274, 110, 66, "MoedaService", ["envio, resgate,", "CupomService"], "plan")
        self.componente(452, 274, 106, 66, "CreditoSemestral", ["Job (APScheduler)"], "plan")
        self.linha([(99, 172), (99, 274)])
        self.seta_aberta((99, 274), (99, 172), 4)
        self.texto(105, 232, "usa", FI, 6, INK)

        # Persistencia
        self.componente(14, 388, 150, 54, "UsuarioRepository", ["BaseRepository[T]", "consultas de alunos/empresas"], "impl")
        self.componente(176, 388, 120, 54, "SQLAlchemy 2 (ORM)", ["entities.py: Usuario, Aluno,", "EmpresaParceira, Endereco,", "InstituicaoEnsino"], "impl")
        self.componente(308, 388, 120, 54, "Alembic", ["migração", "20261026_0001_sprint2"], "impl")
        self.componente(440, 388, 118, 54, "Outros Repositories", ["Professor, Transacao,", "Vantagem"], "plan")
        # Repository -> ORM ; Alembic -> ORM (metadata)
        self.linha([(164, 415), (176, 415)])
        self.seta_aberta((176, 415), (164, 415), 4)
        self.linha([(308, 415), (296, 415)])
        self.seta_aberta((296, 415), (308, 415), 4)
        self.linha([(99, 340), (99, 388)])
        self.seta_aberta((99, 388), (99, 340), 4)
        self.texto(105, 366, "usa", FI, 6, INK)

        # Banco
        self.componente(610, 390, 160, 52, "PostgreSQL (Neon)", ["psycopg 3 · sslmode=require", "SQLite apenas nos testes"], "impl", est="database")
        self.linha([(236, 442), (236, 462), (690, 462), (690, 442)])
        self.seta_aberta((690, 442), (690, 462), 4)
        self.linha([(368, 442), (368, 462)])
        self.texto(480, 459, "SQL (psycopg) · DDL (alembic upgrade head)", FI, 6.2, INK, "c")

        # Transversais
        self.componente(608, 128, 164, 38, "Configuração", ["pydantic-settings · .env"], "impl")
        self.componente(608, 172, 164, 38, "Segurança", ["OAuth2/JWT · bcrypt · perfis"], "plan")
        self.componente(608, 216, 164, 38, "Serviço de e-mail", ["SMTP: moedas, cupom, conferência"], "plan")
        self.componente(608, 260, 164, 38, "Armazenamento de fotos", ["fotos das vantagens"], "plan")
        self.componente(608, 304, 164, 34, "Seed de instituições", ["python -m app.database.seed"], "impl")

        # legenda
        y0 = 482
        self.legenda(0, y0, [("impl", "Implementado na Sprint 2"), ("plan", "Previsto (Sprint 3) — não implementado")])
        self.texto(330, y0 + 6.3, "Borda tracejada = componente previsto. Seta = dependência (usa).", FI, 6.4)
