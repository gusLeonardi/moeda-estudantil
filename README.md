# Conquista — Sistema de Moeda Estudantil

O **Conquista** é uma plataforma acadêmica para reconhecimento do mérito estudantil por meio de moedas virtuais. A proposta é permitir que professores reconheçam a participação e o desempenho dos alunos e que, futuramente, essas moedas sejam trocadas por produtos, descontos e outros benefícios oferecidos por empresas parceiras.

O projeto é desenvolvido na disciplina **Projeto de Software**, do curso de **Engenharia de Software da PUC Minas**, sob orientação da professora **Milena Menezes Adão**.

## Objetivo

Construir uma aplicação web que conecte alunos, professores, instituições de ensino e empresas parceiras em um ecossistema de reconhecimento acadêmico. O desenvolvimento está dividido em três sprints:

- **Sprint 1:** levantamento de requisitos e modelagem UML;
- **Sprint 2:** modelo ER, estratégia de persistência e CRUDs iniciais de alunos e empresas parceiras;
- **Sprint 3:** continuidade das funcionalidades de negócio, autenticação e operações com moedas.

Este repositório contém a implementação da **Sprint 2 — Lab03S02**.

## Funcionalidades

### Implementadas na Sprint 2

- dashboard inicial com indicadores obtidos da API;
- cadastro, listagem, busca, consulta, edição e exclusão de alunos;
- cadastro, listagem, busca, consulta, edição e exclusão de empresas parceiras;
- seleção de instituições de ensino pré-cadastradas no banco;
- validação de CPF, CNPJ, e-mail e campos obrigatórios no front-end e no back-end;
- unicidade de CPF, CNPJ e e-mail;
- CPF e CNPJ não editáveis após o cadastro;
- saldo inicial do aluno igual a zero e protegido contra edição cadastral;
- confirmação antes da exclusão de registros;
- persistência com PostgreSQL e migrações Alembic;
- integração entre o cliente React e a API FastAPI;
- tratamento visual de carregamento, erros e listas vazias.

### Previstas para a Sprint 3

- autenticação e controle de acesso por perfil;
- cadastro e gerenciamento de professores;
- distribuição de moedas aos alunos;
- consulta de saldo e extratos;
- cadastro de vantagens por empresas parceiras;
- resgate de benefícios;
- geração e validação de cupons;
- notificações por e-mail;
- crédito semestral de moedas aos professores.

> As funcionalidades da Sprint 3 ainda não estão implementadas. Os CRUDs atuais são destinados ao desenvolvimento e à avaliação local e não devem ser publicados sem autenticação e autorização.

## Tecnologias

| Camada | Tecnologias |
|---|---|
| Front-end | React, TypeScript, Vite, Tailwind CSS, Axios, React Router, React Hook Form, Zod e Lucide React |
| Back-end | Python 3.13, FastAPI, SQLAlchemy 2, Pydantic, Alembic, psycopg 3 e Uvicorn |
| Banco de dados | PostgreSQL hospedado no Neon |
| Testes | pytest, FastAPI TestClient, Vitest, Testing Library e jsdom |

## Arquitetura

O sistema utiliza um front-end React independente como camada de apresentação e uma API REST em FastAPI:

```text
React → FastAPI Routers → Services → Repositories → SQLAlchemy → PostgreSQL
```

As responsabilidades estão separadas da seguinte forma:

- **React:** interface, navegação, formulários e feedback ao usuário;
- **Routers:** entrada HTTP, injeção de dependências e definição das respostas;
- **Services:** regras de negócio e controle das transações;
- **Repositories:** consultas e operações de acesso a dados;
- **SQLAlchemy:** mapeamento objeto-relacional e persistência;
- **Alembic:** evolução versionada do schema do banco de dados.

Essa organização adapta o padrão MVC definido na modelagem acadêmica: a **View** é implementada pelo cliente React, o **Controller** pelos routers do FastAPI e o **Model** pelas entidades, services e repositories. Não são utilizados templates Jinja2.

## Estrutura do projeto

```text
moeda-estudantil/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── core/
│   │   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── schemas/
│   │   ├── services/
│   │   └── main.py
│   ├── tests/
│   ├── alembic.ini
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── routes/
│   │   ├── services/
│   │   ├── styles/
│   │   ├── test/
│   │   └── types/
│   ├── .env.example
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
├── docs/
│   ├── arquitetura.md
│   ├── modelo-er.md
│   └── modelo-er.mmd
├── .env.example
├── .gitignore
├── Lab03S01-modelagem.pdf
├── LABORATORIO_3_LAB_DESENVOLVIMENTO_DE_SOFTWARE.pdf
└── README.md
```

## Pré-requisitos

Antes de iniciar, instale ou obtenha acesso a:

- [Git](https://git-scm.com/);
- Python 3.13;
- Node.js 22 e npm;
- uma instância PostgreSQL, preferencialmente no [Neon](https://neon.tech/).

## Como executar localmente

Os comandos abaixo foram preparados para **Windows PowerShell**.

### 1. Clonar o repositório

Substitua `<URL_DO_REPOSITORIO>` pela URL disponibilizada pela equipe:

```powershell
git clone <URL_DO_REPOSITORIO>
Set-Location .\moeda-estudantil
```

### 2. Preparar o ambiente Python

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\backend\requirements.txt
```

Se a política do PowerShell impedir a ativação do ambiente virtual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. Configurar o banco PostgreSQL

O backend carrega o arquivo `.env` da **raiz do repositório**. Copie o exemplo existente:

```powershell
Copy-Item .\.env.example .\.env
```

Edite o arquivo `.env` e informe a URL da sua instância Neon:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:senha@host/neondb?sslmode=require
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

O arquivo `.env` contém credenciais e está ignorado pelo Git. Não o envie ao repositório. Caso o Neon forneça uma URL iniciada por `postgresql://`, altere o esquema para `postgresql+psycopg://`, mantendo os demais parâmetros e `sslmode=require`.

### 4. Executar migrações e seed

Com o ambiente virtual ativo:

```powershell
Set-Location .\backend
alembic upgrade head
python -m app.database.seed
```

O seed é idempotente e cadastra somente instituições ainda inexistentes, incluindo PUC Minas, UFMG e CEFET-MG.

### 5. Iniciar a API

Ainda no diretório `backend`:

```powershell
uvicorn app.main:app --reload --port 8000
```

Endereços disponíveis:

- API: `http://localhost:8000`;
- documentação Swagger: `http://localhost:8000/docs`;
- verificação de saúde: `http://localhost:8000/health`.

### 6. Preparar e iniciar o front-end

Abra outro terminal PowerShell e execute a partir da raiz clonada:

```powershell
Set-Location .\frontend
npm install
Copy-Item .\.env.example .\.env
npm run dev
```

O arquivo `frontend/.env` deve conter:

```dotenv
VITE_API_URL=http://localhost:8000/api
```

Acesse a aplicação em `http://localhost:5173`.

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/api/alunos` | Lista alunos e aceita o parâmetro `busca` |
| `GET` | `/api/alunos/{id}` | Consulta um aluno |
| `POST` | `/api/alunos` | Cadastra um aluno |
| `PUT` | `/api/alunos/{id}` | Atualiza um aluno |
| `DELETE` | `/api/alunos/{id}` | Exclui um aluno |
| `GET` | `/api/empresas` | Lista empresas e aceita o parâmetro `busca` |
| `GET` | `/api/empresas/{id}` | Consulta uma empresa |
| `POST` | `/api/empresas` | Cadastra uma empresa |
| `PUT` | `/api/empresas/{id}` | Atualiza uma empresa |
| `DELETE` | `/api/empresas/{id}` | Exclui uma empresa |
| `GET` | `/api/instituicoes` | Lista instituições de ensino |

## Modelo de dados

As entidades implementadas na Sprint 2 são:

- **Usuario:** concentra nome, e-mail, tipo e a estrutura preparada para futura autenticação;
- **Aluno:** contém CPF, RG, curso, saldo e vínculo obrigatório com uma instituição;
- **EmpresaParceira:** contém CNPJ e telefone;
- **InstituicaoEnsino:** mantém as instituições disponíveis para seleção;
- **Endereco:** representa o endereço associado a um usuário.

`Aluno` e `EmpresaParceira` especializam `Usuario`. Cada usuário possui um endereço, e cada aluno está vinculado a uma instituição de ensino. O banco também aplica restrições de unicidade e chaves estrangeiras.

Documentação detalhada:

- [Modelo Entidade-Relacionamento](docs/modelo-er.md);
- [Diagrama ER em Mermaid](docs/modelo-er.mmd);
- [Arquitetura do sistema](docs/arquitetura.md).

## Testes

### Back-end

A suíte utiliza um banco SQLite isolado criado exclusivamente durante os testes. A instância Neon configurada no `.env` não é alterada.

Na raiz do projeto:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q
```

Os testes cobrem os CRUDs, duplicidade de documentos e e-mails, instituição inexistente, buscas, consultas e exclusões.

### Front-end

No diretório `frontend`:

```powershell
npm test
npm run build
```

`npm test` executa os testes com Vitest. `npm run build` também verifica os tipos TypeScript e gera o build de produção.

### Verificação manual dos CRUDs

1. Inicie o backend e o frontend em terminais separados.
2. Execute o seed e confirme que as instituições aparecem no formulário de aluno.
3. Cadastre um aluno e uma empresa parceira.
4. Confira os registros nas listagens e nas páginas de detalhes.
5. Edite os registros e verifique que CPF e CNPJ continuam bloqueados.
6. Tente reutilizar CPF, CNPJ ou e-mail e confirme a mensagem de conflito.
7. Exclua os registros e confirme que a interface solicita confirmação.
8. Recarregue a página para verificar a persistência dos dados.

## Documentação acadêmica

- [Modelagem UML da Sprint 1](Lab03S01-modelagem.pdf);
- [Enunciado do Laboratório 3](LABORATORIO_3_LAB_DESENVOLVIMENTO_DE_SOFTWARE.pdf);
- [Modelo ER da Sprint 2](docs/modelo-er.md);
- [Diagrama ER em Mermaid](docs/modelo-er.mmd);
- [Decisões de arquitetura](docs/arquitetura.md).

## Equipe

- Felipe Costa Lisboa
- Arthur Martins Candido
- Gustavo Leonardi Ribeiro
- Sofia Fernandes Ferreira Silva

## Estado atual

A **Sprint 2 está implementada**, incluindo a estrutura de persistência, migrações, seed, integração entre front-end e back-end e CRUDs iniciais de alunos e empresas parceiras.

A **Sprint 3 está prevista** para completar autenticação, professores e os fluxos relacionados a moedas, extratos, vantagens, resgates, cupons e notificações.
