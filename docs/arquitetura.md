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

## Segurança e limites

Senhas são armazenadas com Argon2id; JWT HS256 expira em 30 minutos. Segredos são configurados por ambiente. As rotas usam autorização por perfil e identificador autenticado nas operações financeiras. Detalhes e matriz pública/privada constam no README Release 02.

Crédito semestral e provisionamento de professor exigem ADMIN_CRON_TOKEN; alunos e empresas fazem cadastro com senha; contas antigas ativam por token enviado ao e-mail, guardado como hash, expirável e de uso único.

Débitos usam atualizações condicionais no banco (`saldo >= valor`) para impedir saldo negativo sob concorrência. Services coordenam `commit` e `rollback`, enquanto chaves de idempotência impedem o processamento repetido de um resgate.
