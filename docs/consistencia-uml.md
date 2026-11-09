# Consistência com os modelos UML da Sprint 1

## Resultado da revisão

Os diagramas Mermaid da Sprint 3 são consistentes com o núcleo cadastral dos modelos UML existentes. Eles representam um recorte da arquitetura e do domínio originais, não uma substituição do modelo completo planejado.

## Rastreabilidade do domínio

| UML da Sprint 1 | Sprint 3 | Situação |
|---|---|---|
| `Usuario` como superclasse | tabela `usuarios` e entidade `Usuario` | Preservado |
| `Aluno` especializa `Usuario` | PK/FK `alunos.usuario_id` | Preservado |
| `EmpresaParceira` especializa `Usuario` | PK/FK `empresas_parceiras.usuario_id` | Preservado |
| aluno possui endereço | relação `Usuario` 1:1 `Endereco` | Preservado no agregado do usuário |
| aluno pertence a instituição | FK obrigatória `instituicao_id` | Preservado |
| aluno inicia com saldo zero | `saldo` com valor padrão `0.00` | Preservado |
| CPF e e-mail únicos | restrições de banco e validação de serviço | Preservado |
| CNPJ e e-mail únicos | restrições de banco e validação de serviço | Preservado |
| CPF não muda na edição | ausente de `AlunoUpdate` | Preservado |
| cadastro de empresa | CRUD de empresa parceira | Preservado |

## Rastreabilidade arquitetural

| UML de componentes | Implementação da Sprint 3 | Avaliação |
|---|---|---|
| Controllers em routers FastAPI | `routers/api.py` | Correspondência direta |
| Validação com Pydantic | schemas de aluno, empresa e endereço | Correspondência direta |
| Regras nos Services | `AlunoService`, `EmpresaService` e `DashboardService` | Correspondência direta |
| Repositories/DAO com SQLAlchemy | `UsuarioRepository` e `BaseRepository` | Correspondência predominante, com ressalva abaixo |
| ORM SQLAlchemy | entidades declarativas tipadas | Correspondência direta |
| Migrações Alembic | revisão inicial e configuração de metadata | Correspondência direta |
| PostgreSQL | conexão configurável para o Neon | Correspondência direta |
| Servidor Uvicorn | execução de `app.main:app` | Correspondência direta |

## Adaptação do MVC

O UML da Sprint 1 propunha templates Jinja2 como View. A Sprint 3 usa React como cliente independente porque a stack efetivamente adotada inclui React, TypeScript e Vite. Essa mudança não altera as responsabilidades do MVC:

- View: React;
- Controller: routers FastAPI;
- Model: services, repositories, entidades SQLAlchemy e PostgreSQL.

A comunicação entre View e Controller passou a ocorrer por HTTP/JSON, em vez de renderização de templates no servidor.

## Elementos deliberadamente fora do recorte

O modelo UML completo também contém `Professor`, `Vantagem`, `Transacao`, `TransacaoEnvio`, `TransacaoResgate`, autenticação, agendamento e serviço de e-mail. Esses elementos não aparecem nos diagramas de implementação da Sprint 3 porque o escopo atual autoriza somente os CRUDs finais de alunos e empresas, arquitetura e persistência.

O campo nullable `senha_hash` permanece em `Usuario` como preparação estrutural, mas não representa autenticação implementada. Os diagramas não mostram login, JWT ou controle de acesso para evitar indicar uma proteção inexistente.

## Observação sobre Repository

O UML define Repository/DAO como camada de acesso ao banco. Os diagramas seguem esse fluxo. Na implementação atual, as consultas de listagem, busca, detalhes, instituição, e-mail duplicado e indicadores estão no repository. Entretanto, `AlunoService` e `EmpresaService` ainda consultam CPF/CNPJ e executam `add`/`delete` diretamente pela sessão SQLAlchemy. Isso constitui uma aderência parcial ao padrão Repository, embora não altere o comportamento funcional.

A delimitação da transação (`commit` e `rollback`) permanece corretamente no service, coerente com sua responsabilidade de coordenar a operação de negócio. Para aderência estrita ao UML, as consultas de documento e os comandos de persistência podem ser movidos ao repository em uma refatoração futura, mantendo a transação no service.

## Conclusão

Não há conflito estrutural entre os Mermaid da Sprint 3 e o UML original. As diferenças principais são decisões explícitas: React substitui Jinja2 na View e o conjunto de entidades foi reduzido ao escopo cadastral autorizado. A única divergência técnica identificada é a aderência ainda parcial ao Repository em alguns comandos dos services.
