# Auditoria técnica da Sprint 3

## Escopo revisado

Foram analisados README, estrutura das aplicações, models SQLAlchemy, schemas Pydantic, routers, services, repositories, migração Alembic, testes, modelo ER e integração React/API.

## Correções aplicadas

- validação completa dos dígitos verificadores de CPF e CNPJ no backend e frontend;
- testes de documentos inválidos, duplicidades, recursos inexistentes e campos imutáveis;
- busca de alunos por nome, e-mail, CPF, curso e instituição;
- busca de empresas por nome, e-mail e CNPJ;
- endpoint agregado de indicadores para evitar baixar listagens completas no dashboard;
- documentação expandida de arquitetura, persistência e demonstração;
- atualização do escopo para o Lab03S03 atual.

## Aspectos preservados

- arquitetura React, routers, services, repositories, SQLAlchemy e PostgreSQL;
- especialização relacional de aluno e empresa por `Usuario`;
- CPF, CNPJ e saldo ausentes dos schemas de atualização;
- transação por operação com rollback de conflitos;
- configuração do Neon exclusivamente por variável de ambiente;
- migração existente, pois as correções não alteraram o schema.

## Riscos conhecidos

- a API ainda não possui autenticação ou autorização, deliberadamente fora do escopo;
- os testes frontend cobrem validação e interpretação de erros, mas ainda não executam fluxos completos no navegador;
- o campo `senha_hash` permanece nullable e sem uso até uma sprint futura autorizada;
- o frontend depende da disponibilidade da API e não oferece operação offline.

## Verificações executadas

- backend: `10 passed` com pytest e SQLite isolado;
- frontend: `4 passed` com Vitest;
- produção: TypeScript e build Vite concluídos;
- banco remoto: nenhuma operação executada.
