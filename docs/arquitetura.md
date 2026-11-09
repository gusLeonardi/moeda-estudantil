# Arquitetura do sistema

## Visão geral

O Conquista usa um cliente React separado de uma API REST FastAPI. A separação permite evoluir interface e servidor de forma independente, mantendo contratos HTTP tipados nas duas pontas.

Arquivos-fonte dos diagramas:

- [Arquitetura em camadas](arquitetura-camadas.mmd);
- [Diagrama de componentes](componentes.mmd);
- [Sequência do cadastro de aluno](sequencia-cadastro-aluno.mmd);
- [Visão de implantação](implantacao.mmd);
- [Modelo entidade-relacionamento](modelo-er.mmd).
- [Matriz de consistência com os modelos UML](consistencia-uml.md).

```text
Navegador
  React + TypeScript + Zod
          |
          | HTTP/JSON
          v
FastAPI Routers + Pydantic
          |
          v
       Services
          |
          v
     Repositories
          |
          v
SQLAlchemy 2 + PostgreSQL (Neon)
```

## Responsabilidades das camadas

### Apresentação

O diretório `frontend/src` contém páginas, componentes reutilizáveis, rotas e clientes HTTP. React Router controla a navegação, React Hook Form mantém o estado dos formulários e Zod valida dados antes do envio. Axios centraliza a URL da API, o timeout e a interpretação de erros.

O frontend não aplica regras que substituem o servidor. A validação duplicada de CPF, CNPJ, e-mail e campos obrigatórios melhora a experiência, mas a API continua sendo a autoridade.

### Routers

`backend/app/routers/api.py` define recursos, métodos HTTP, parâmetros de busca, status de resposta e schemas públicos. A dependency `get_db` fornece uma sessão SQLAlchemy por requisição e garante seu fechamento.

### Services

`backend/app/services/crud.py` concentra regras de negócio: existência da instituição, imutabilidade indireta de CPF/CNPJ, saldo fora dos schemas de escrita, normalização de e-mail e tradução de conflitos de persistência. Cada operação de escrita confirma uma única transação. Falhas de integridade causam rollback.

### Repositories

`backend/app/repositories` encapsula consultas SQLAlchemy. Os serviços não montam detalhes de busca e carregamento de relacionamentos. `selectinload` evita consultas repetidas ao serializar endereços, instituições e especializações.

### Models e banco

`backend/app/models/entities.py` mapeia tabelas, chaves, relacionamentos e restrições. Alembic mantém a evolução versionada do schema. PostgreSQL garante unicidade e integridade referencial mesmo quando duas requisições concorrentes ultrapassam validações prévias.

## Adaptação do MVC

A arquitetura preserva as responsabilidades do MVC sem usar templates no servidor:

| MVC | Implementação no Conquista |
|---|---|
| View | React, páginas, componentes e formulários |
| Controller | Routers FastAPI e contratos Pydantic |
| Model | Services, repositories, entidades SQLAlchemy e PostgreSQL |

Services e repositories refinam o Model para evitar controllers com regras de negócio ou consultas acopladas ao protocolo HTTP.

## Comunicação HTTP/REST

O cliente envia e recebe JSON sob o prefixo `/api`. Criação retorna `201`, exclusão bem-sucedida retorna `204`, recursos inexistentes retornam `404`, duplicidades retornam `409` e payloads inválidos retornam `422`. A interface converte essas respostas em mensagens ao usuário sem expor detalhes internos.

Os recursos da Sprint 3 são:

- `/api/alunos` e `/api/alunos/{id}`;
- `/api/empresas` e `/api/empresas/{id}`;
- `/api/instituicoes`;
- `/api/dashboard/indicadores`.

## Segurança e limites

Credenciais ficam em `.env`, ignorado pelo Git. CORS aceita somente origens configuradas. A URL do banco não aparece em respostas ou logs da aplicação. Os CRUDs ainda não possuem autenticação e devem permanecer em ambiente acadêmico controlado.

Professores, autenticação, transações, moedas, vantagens e resgates estão fora desta Sprint 3. O campo `senha_hash` apenas preserva compatibilidade com a modelagem anterior e não representa um fluxo de login implementado.
