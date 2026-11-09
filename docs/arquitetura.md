# Persistência — Sprint 3

O Conquista usa PostgreSQL no Neon, SQLAlchemy 2.x e Alembic. O fluxo de persistência separa Routers, Services e Repositories, com transações `commit`/`rollback`.

## Entidades

- `Usuario`, `Endereco`, `InstituicaoEnsino`, `Aluno`, `Professor`, `EmpresaParceira`.
- `TransferenciaMoedas`: professor, aluno, quantidade, justificativa e data.
- `Vantagem`: empresa, nome, descrição, custo, imagem opcional e estado ativo.
- `ResgateVantagem`: aluno, vantagem, empresa, custo, cupom único, chave idempotente e utilização.
- `CreditoSemestral`: professor, ano, semestre, quantidade e data; unicidade por professor/ano/semestre.

## Integridade

- `Numeric(14,2)` para saldos e valores.
- Atualização atômica de saldos nas transferências e resgates.
- Registro do cupom no banco antes do envio de e-mail.
- `ON CONFLICT DO NOTHING` no crédito semestral, evitando dupla concessão no mesmo período.
- Migrações até `20261109_0005_creditos_semestrais.py`.

## Limitações

Não há autenticação ou agendamento automático de crédito. O envio de e-mail ocorre após o `commit` e uma falha SMTP não desfaz a transação. Consulte `modelagem/Lab03S03-modelagem-atualizada.md` para rastreabilidade.
