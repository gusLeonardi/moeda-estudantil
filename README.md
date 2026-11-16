# Conquista — Sistema de Moeda Estudantil

O **Conquista** é uma aplicação acadêmica para reconhecimento do mérito estudantil por meio de moedas virtuais. Professores podem reconhecer a participação e o desempenho dos alunos; alunos podem usar o saldo para resgatar vantagens oferecidas por empresas parceiras.

Projeto desenvolvido na disciplina **Projeto de Software**, do curso de **Engenharia de Software da PUC Minas**, sob orientação da professora **Milena Menezes Adão**.

## Situação do projeto

As entregas das Sprints 1, 2 e 3 e do Lab04 (Release 02) estão implementadas. O sistema conta com autenticação e autorização por perfil, operações financeiras, vantagens, cupons, administração institucional de professores e documentação UML.

O sistema está publicado em produção. Os endereços estão na seção [Sistema em Produção](#sistema-em-produção).

## Histórico das entregas

- **Sprint 1:** levantamento de requisitos e modelagem UML.
- **Sprint 2:** modelo Entidade-Relacionamento, persistência e CRUDs iniciais de alunos e empresas parceiras.
- **Sprint 3 — Lab03S03:** conclusão dos CRUDs, arquitetura em camadas, persistência e apresentação.
- **Release 02 — Lab04S01:** autenticação, autorização, isolamento de dados, fluxos financeiros, ativação de contas antigas e diagramas UML.
- **Release 02 — Lab04S02:** preparação de configuração de implantação, documentação e diagrama de implantação.

## Funcionalidades por perfil

### Aluno

- Cadastro público de visitante com senha e validações de dados.
- Consulta e edição do próprio perfil e do próprio extrato.
- Consulta do catálogo de vantagens ativas.
- Resgate de vantagem, com débito transacional e geração de cupom.
- Consulta do histórico de movimentações e dos cupons recebidos.

O aluno autenticado não pode criar outra conta nem consultar ou alterar dados privados de outros alunos.

### Professor

- Conta pré-cadastrada pela instituição; não há cadastro público de professores.
- Consulta de alunos para apoiar os fluxos acadêmicos, sem permissão para editar seus cadastros.
- Transferência de moedas para alunos e consulta do próprio extrato.
- Consulta do histórico de créditos semestrais e dos indicadores disponíveis ao perfil.

O saldo inicial do professor é de **1.000 moedas**. Cada crédito semestral acrescenta **1.000 moedas**, com registro por professor, ano e semestre para impedir duplicidade.

### Empresa parceira

- Cadastro público para visitantes, com senha e validação dos dados empresariais.
- Consulta e edição do próprio perfil.
- Criação e gerenciamento das próprias vantagens, incluindo ativação, desativação e exclusão quando não há resgates associados.
- Consulta e validação dos cupons emitidos para suas vantagens.

As imagens das vantagens usam URL externa validada. Cada vantagem tem uma empresa proprietária; empresas não podem gerenciar vantagens nem consultar cupons de outras empresas.

### Administrador institucional

- Acesso por tela administrativa com credenciais provisionadas no servidor.
- Cadastro, listagem, pesquisa, consulta e edição de professores.
- Pré-cadastro sem senha e envio ou reenvio de convite para ativação.

Não há autocadastro administrativo. A credencial administrativa é distinta do token interno usado para operações de cron.

## Regras de negócio principais

- Senhas são armazenadas com hash Argon2; novas senhas devem ter ao menos 12 caracteres.
- Tokens JWT são assinados com HS256, têm validade limitada e carregam o perfil do usuário. Os endpoints também verificam o perfil e a identidade no servidor.
- Transferências e resgates são processados em transações para evitar saldo parcial ou negativo. A origem da transferência e o aluno do resgate são derivados do JWT, não dos identificadores enviados pelo navegador.
- Uma chave de idempotência impede que uma repetição do mesmo pedido de resgate faça outro débito. Cada resgate gera um cupom único.
- Uma empresa só consulta ou valida cupons vinculados a vantagens de sua propriedade; um cupom só pode ser utilizado uma vez.
- O histórico é preservado: vantagens com resgates associados não podem ser excluídas e devem ser desativadas.
- Créditos semestrais são idempotentes por professor e período.
- Contas antigas sem senha podem solicitar ativação. O token é enviado ao e-mail já cadastrado, armazenado no banco somente como hash, expira em 15 minutos e é invalidado após o uso. Informar apenas CPF ou e-mail não ativa uma conta.
- Login, solicitação de ativação e operações administrativas de provisionamento têm limitação de tentativas armazenada no banco.
- O token administrativo de cron (`ADMIN_CRON_TOKEN`) é validado somente pelo back-end e não é enviado ao navegador.

## Arquitetura e tecnologias

```text
Navegador (React/Vite) → API REST (FastAPI) → Services → Repositories → SQLAlchemy → PostgreSQL (Neon)
```

| Camada | Tecnologias e responsabilidades |
|---|---|
| Interface web | React 18, TypeScript, Vite, Tailwind CSS, React Router, React Hook Form, Zod, Axios e Lucide React |
| API | Python, FastAPI, Pydantic e Uvicorn |
| Regras de negócio | Services para autenticação, autorização, saldos, vantagens, resgates e cupons |
| Persistência | Repositories, SQLAlchemy 2, PostgreSQL e psycopg 3 |
| Migrações | Alembic |
| Testes | pytest, FastAPI TestClient, Vitest, Testing Library e jsdom |
| Hospedagem de produção | Render para a interface e a API; PostgreSQL no Neon |

Os routers tratam HTTP e dependências; os services aplicam regras de negócio e coordenam transações; os repositories concentram consultas e operações de persistência. No modelo MVC acadêmico, o React corresponde à View, os routers ao Controller e as entidades e camadas de domínio ao Model.

## Sistema em Produção

- **Aplicação web — React, TypeScript e Vite:** [https://conquista-front.onrender.com](https://conquista-front.onrender.com)
- **API — FastAPI:** [https://conquista-api-dzln.onrender.com](https://conquista-api-dzln.onrender.com)
- **Verificação de saúde da API:** [https://conquista-api-dzln.onrender.com/health](https://conquista-api-dzln.onrender.com/health)
- **Documentação interativa da API:** [https://conquista-api-dzln.onrender.com/docs](https://conquista-api-dzln.onrender.com/docs)
- **Banco de dados:** PostgreSQL no Neon.
- **Hospedagem:** Render, plano gratuito.

As credenciais de produção são configuradas nos painéis dos provedores e não fazem parte deste repositório. O frontend acessa a API pela variável pública `VITE_API_URL`; essa variável não deve conter segredos.

## Estrutura do repositório

```text
moeda-estudantil/
├── backend/
│   ├── alembic/versions/       # Migrações do banco
│   ├── app/
│   │   ├── core/               # Configurações
│   │   ├── database/           # Conexão e dados iniciais
│   │   ├── models/             # Entidades SQLAlchemy
│   │   ├── repositories/       # Acesso a dados
│   │   ├── routers/            # Endpoints FastAPI
│   │   ├── schemas/            # Validação e respostas
│   │   └── services/           # Regras de negócio
│   ├── scripts/                # Ferramentas administrativas locais
│   ├── tests/                  # Testes automatizados
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── auth/               # Sessão e rotas protegidas
│   │   ├── components/
│   │   ├── pages/
│   │   ├── routes/
│   │   └── services/           # Integração com a API
│   ├── .env.example
│   ├── package.json
│   └── vercel.json             # Regras de build e navegação SPA
├── docs/
│   ├── modelagem/              # Fontes PlantUML e imagens
│   ├── implantacao-lab04s02.md
│   ├── arquitetura.md
│   └── modelo-er.md
├── render.yaml                 # Serviço da API no Render
├── .env.example
└── README.md
```

## Execução local

As instruções abaixo usam Windows PowerShell. Requisitos: Git, Python 3.13, Node.js 22 com npm e um banco PostgreSQL. Para desenvolvimento, pode-se usar um banco local isolado ou uma instância própria do Neon. **Não use a base de produção para testes ou migrações locais.**

### 1. Preparar o back-end

Na raiz do repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt
Copy-Item .\.env.example .\.env
```

Edite `.env`, na raiz, com a conexão do banco local ou isolado e valores próprios de desenvolvimento. Exemplo sem credenciais reais:

```dotenv
DATABASE_URL=postgresql+psycopg://<usuario>:<senha>@<host>/<banco>?sslmode=require
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
APP_ENV=development
JWT_SECRET=<segredo-local-aleatorio>
ADMIN_CRON_TOKEN=<token-interno-local-aleatorio>
ADMIN_UI_USERNAME=<usuario-administrativo-local>
ADMIN_UI_PASSWORD_HASH=<hash-argon2-gerado-localmente>
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASSWORD=
SMTP_FROM=
```

Em desenvolvimento, o e-mail é opcional, mas a ativação de contas e as notificações dependem de um serviço SMTP configurado. Gere o hash da senha administrativa sem armazenar a senha no projeto:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe .\scripts\hash_admin_password.py
```

Configure `ADMIN_UI_PASSWORD_HASH` no `.env` apenas para o ambiente local. Em produção, `JWT_SECRET` e `ADMIN_CRON_TOKEN` devem ser segredos diferentes, aleatórios e com pelo menos 32 bytes. Não coloque segredos em variáveis `VITE_*`.

### 2. Aplicar migrações e iniciar a API

No diretório `backend`:

```powershell
Set-Location .\backend
..\.venv\Scripts\alembic.exe upgrade head
..\.venv\Scripts\python.exe -m app.database.seed
..\.venv\Scripts\uvicorn.exe app.main:app --reload --port 8000
```

A API estará em `http://localhost:8000`; a documentação Swagger em `http://localhost:8000/docs`; e a verificação de saúde em `http://localhost:8000/health`.

O seed cadastra as instituições que ainda não existirem. Execute-o somente no banco local ou isolado escolhido para desenvolvimento.

### 3. Iniciar o front-end

Em outro terminal, a partir da raiz:

```powershell
Set-Location .\frontend
npm ci
Copy-Item .\.env.example .\.env
npm run dev
```

O arquivo `frontend/.env` deve apontar para a API local:

```dotenv
VITE_API_URL=http://localhost:8000/api
```

A aplicação estará em `http://localhost:5173`.

### Variáveis de ambiente

| Variável | Uso |
|---|---|
| `DATABASE_URL` | Conexão PostgreSQL usada pelo back-end; em produção, exigir TLS (`sslmode=require` ou superior). |
| `CORS_ORIGINS` | Lista separada por vírgulas das origens autorizadas. Em produção, usar somente origens HTTPS explícitas. |
| `APP_ENV` | Ambiente, por exemplo `development` ou `production`. |
| `JWT_SECRET` | Segredo privado usado para assinar JWTs. |
| `ADMIN_CRON_TOKEN` | Segredo privado para operações internas de cron/provisionamento. |
| `ADMIN_UI_USERNAME` | Nome da conta administrativa institucional. |
| `ADMIN_UI_PASSWORD_HASH` | Hash Argon2 da senha administrativa; nunca a senha em texto puro. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Configuração opcional de envio de e-mail. |
| `VITE_API_URL` | URL pública da API consumida pelo frontend, por exemplo `https://<dominio-da-api>/api`. Não pode conter segredos. |

Os nomes dos parâmetros são mostrados para documentação; configure valores somente em arquivos locais ignorados pelo Git ou nos painéis privados dos serviços. Nunca versione `.env` nem credenciais reais.

## Acesso e segurança

Os perfis disponíveis são `ALUNO`, `PROFESSOR`, `EMPRESA` e `ADMIN`. As rotas protegidas validam assinatura e expiração do JWT e conferem o perfil necessário. A API deriva a identidade das operações financeiras da sessão autenticada e aplica validação de propriedade nos dados das empresas.

O cadastro de alunos e empresas é público somente para visitantes sem uma sessão JWT válida. Professores são pré-cadastrados pela administração institucional; o endpoint interno exige `ADMIN_CRON_TOKEN`. A tela administrativa usa credenciais próprias configuradas apenas no back-end e não recebe o token de cron.

O JWT do navegador fica em `sessionStorage`, é removido no logout e em respostas 401. Isso reduz a persistência após fechar a sessão, mas não impede que um ataque XSS na mesma origem leia o token enquanto a sessão estiver ativa. O armazenamento no navegador deve ser considerado um risco residual; mantenha dependências atualizadas e não renderize conteúdo HTML não confiável.

O endpoint de crédito semestral também exige `ADMIN_CRON_TOKEN`. Ele não deve ser exposto a perfis comuns. Os limites de tentativas de autenticação são persistidos no PostgreSQL e usam contadores por IP/e-mail conforme a configuração dos serviços.

## Endpoints principais

A API é prefixada por `/api`. As permissões são conferidas no back-end; a lista abaixo resume os fluxos mais utilizados.

| Método e rota | Acesso e finalidade |
|---|---|
| `POST /api/auth/login` | Público; autentica aluno, professor ou empresa. |
| `POST /api/auth/activation/request` | Público; solicita token para conta elegível sem senha. |
| `POST /api/auth/activation/complete` | Público; define senha com token temporário. |
| `POST /api/alunos`, `POST /api/empresas` | Cadastro público para visitantes; JWT autenticado é recusado. |
| `GET /api/instituicoes` | Público; opções de instituição para os formulários. |
| `GET/PUT /api/alunos/{id}` e `GET /api/alunos/{id}/extrato` | Perfil ALUNO; somente os próprios dados. Professores podem consultar a listagem de alunos. |
| `POST /api/moedas/transferencias` | Perfil PROFESSOR; identidade de origem derivada do JWT. |
| `GET /api/professores/{id}/extrato` | Perfil PROFESSOR; somente o próprio extrato. |
| `GET /api/vantagens/catalogo` | Perfil ALUNO; vantagens ativas disponíveis. |
| `POST /api/resgates` | Perfil ALUNO; resgate idempotente. |
| `GET /api/vantagens/minhas` e `POST/PUT/DELETE /api/vantagens` | Perfil EMPRESA; gerenciamento limitado às próprias vantagens. Há rotas para ativar e desativar. |
| `POST /api/cupons/consultar`, `POST /api/cupons/validar` | Perfil EMPRESA; apenas cupons das próprias vantagens. |
| `GET/POST/PUT /api/admin/professores` | Administrador autenticado; gerenciamento institucional de professores. |
| `POST /api/moedas/creditos-semestrais` | Operação interna protegida por `X-Admin-Token` / `ADMIN_CRON_TOKEN`. |
| `GET /health` | Público; verificação de disponibilidade da API. |

Consulte `/docs` para os parâmetros e modelos completos da API.

## Testes e validações

Os testes de back-end usam uma base isolada configurada pela suíte; não devem apontar para o PostgreSQL de produção.

### Back-end

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q
```

### Front-end

```powershell
Set-Location .\frontend
npm test
npm run build
```

Na última validação registrada em `docs/implantacao-lab04s02.md`: **43 testes de back-end aprovados**, **19 testes de front-end aprovados** e build do front-end concluído com sucesso. Essa validação não foi repetida durante a edição deste README.

A cadeia de migrações também foi aplicada em uma base SQLite descartável para verificar o fluxo de migração e a preservação de usuários legados sem senha. O teste de migração em PostgreSQL isolado não foi executado no registro citado: `psql` não estava disponível e o Docker não iniciou. Não execute `alembic upgrade head` contra o Neon compartilhado sem revisão e autorização.

## Diagramas e documentação acadêmica

Os fontes editáveis PlantUML e as imagens PNG correspondentes ficam em [`docs/modelagem`](docs/modelagem). Os diagramas do Lab04 incluem:

- `lab04-seq-autenticacao.puml` e `.png` — login, ativação de contas antigas e limites de tentativas;
- `lab04-seq-transferencia.puml` e `.png` — transferência de moedas;
- `lab04-seq-resgate.puml` e `.png` — resgate, transação e idempotência;
- `lab04-seq-cupom.puml` e `.png` — consulta e validação de cupom pela empresa proprietária;
- `lab04-seq-admin-professores.puml` e `.png` — pré-cadastro e gerenciamento administrativo de professores;
- `lab04-sequencias.puml` e `.png` — sequência integrada dos fluxos por perfil;
- `lab04-visao-geral-interacao.puml` e `.png` — Diagrama de Visão Geral de Interação UML com decisões e referências às sequências;
- `lab04-diagrama-implantacao.puml` e `.png` — navegador, frontend, API, PostgreSQL e SMTP. O diagrama identifica os provedores como planejados quando descreve a arquitetura-alvo e não afirma implantação que não esteja verificada.

O PDF consolidado está em [`output/pdf/conquista-lab04-diagramas-uml.pdf`](output/pdf/conquista-lab04-diagramas-uml.pdf). A modelagem anterior das Sprints 1 a 3 também está em `docs/`, nos arquivos de modelo ER, arquitetura, persistência, fluxos e apresentação.

## Créditos

Projeto da disciplina **Projeto de Software — PUC Minas**.

- **Orientadora:** professora Milena Menezes Adão.
- **Equipe:**
  - Felipe Costa Lisboa;
  - Arthur Martins Candido;
  - Gustavo Leonardi Ribeiro;
  - Sofia Fernandes Ferreira Silva.

## Licença

Projeto acadêmico. Consulte a equipe responsável antes de reutilizar ou redistribuir o sistema.
