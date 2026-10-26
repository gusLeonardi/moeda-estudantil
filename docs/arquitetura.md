# Arquitetura

```text
React (View) → FastAPI Router (Controller) → Service → Repository/SQLAlchemy → PostgreSQL Neon
```

A View do MVC é um cliente React independente, substituindo os templates Jinja2 propostos no diagrama de componentes da Sprint 1 conforme a stack exigida para esta entrega. Os routers tratam HTTP e injeção de sessão; services aplicam regras e transações; repositories encapsulam consultas; models definem persistência e restrições. Pydantic e Zod validam as duas fronteiras.

O pool usa `pool_pre_ping`; sessões são encerradas pela dependency `get_db`; conflitos de integridade provocam rollback e resposta 409 sem detalhes internos. CORS permite apenas origens definidas por `CORS_ORIGINS`.

## Segurança e produção

Os CRUDs da Sprint 2 não têm autenticação. Portanto, a API não deve ser publicada até receber autenticação e autorização por papéis. `senha_hash` é nullable e não é exposto; quando autenticação for implementada, apenas hashes fortes devem ser armazenados. A aplicação nunca registra a URL do banco.
