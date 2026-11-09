# Roteiro da apresentação — 20 minutos

| Tempo | Conteúdo | Demonstração |
|---:|---|---|
| 1 min | Contexto e objetivo da Sprint 3 | Escopo final dos CRUDs |
| 3 min | Arquitetura | Fluxo React, FastAPI, services, repositories e PostgreSQL |
| 3 min | Persistência | Modelo ER, restrições, sessões, rollback e Alembic |
| 4 min | CRUD de alunos | Cadastro, instituição, busca, detalhes, edição e exclusão |
| 3 min | CRUD de empresas | Cadastro, busca, edição, duplicidade e exclusão |
| 3 min | Tutorial das tecnologias | Zod/Pydantic, Axios, SQLAlchemy e testes isolados |
| 2 min | Qualidade | Testes, build, tratamento de erros e responsividade |
| 1 min | Encerramento | Limites da sprint e próximos passos autorizados |

## Checklist da demonstração

1. Abrir o dashboard e confirmar os indicadores vindos de `/api/dashboard/indicadores`.
2. Cadastrar um aluno com instituição pré-cadastrada.
3. Tentar um CPF inválido e um e-mail duplicado.
4. Buscar o aluno por nome, CPF, curso ou instituição.
5. Editar o aluno e mostrar CPF e saldo protegidos.
6. Excluir o aluno após a confirmação.
7. Repetir o fluxo principal para empresa e demonstrar CNPJ inválido/duplicado.
8. Exibir Swagger, testes automatizados e migração Alembic.

Use uma base local ou descartável durante a apresentação. Não demonstre operações de escrita no banco Neon com dados reais.
