# Conquista — Modelagem atualizada para a Sprint 3

> Complemento de implementação ao documento histórico `Lab03S01-modelagem-atualizada.pdf`. Os identificadores e critérios originais da Sprint 1 foram preservados; a avaliação abaixo reflete o código entregue no ZIP em 09/11/2026.

## 1. Escopo e arquitetura

Frontend React/TypeScript → API FastAPI (routers + schemas Pydantic) → Services → Repositories → SQLAlchemy → PostgreSQL (Neon). Alembic controla migrações. O serviço SMTP usa Gmail configurado por variáveis de ambiente. Não há autenticação/autorização.

## 2. Matriz de rastreabilidade — Casos de uso

| UC | Caso de uso | Situação Sprint 3 | Evidência / ressalva |
|---|---|---|---|
| UC01 | Autenticar | Não implementado | Sem login, sessão ou autorização por perfil. |
| UC02 | Cadastrar aluno | Parcial | CRUD, instituição e validações; sem login/senha. |
| UC03 | Gerenciar perfil do aluno | Parcial | CRUD disponível, sem controle de titularidade. |
| UC04 | Cadastrar empresa parceira | Parcial | CRUD e validações; sem login/senha. |
| UC05 | Gerenciar empresa | Parcial | CRUD disponível, sem controle de titularidade. |
| UC06 | Cadastrar vantagem | Parcial | CRUD e desativação; foto opcional, sem empresa autenticada. |
| UC07 | Listar vantagens | Parcial | Listagem e custo; foto opcional e sem sessão autenticada. |
| UC08 | Enviar moedas | Parcial | Transferência atômica, saldo e motivo; não foi localizada regra de mesma instituição nem autenticação. |
| UC09 | Consultar extrato | Implementado sem login | Extratos de aluno e professor por ID; aluno inclui resgates. |
| UC10 | Trocar moedas por vantagem | Implementado sem login | Débito atômico, cupom único e tentativa de notificação; sem autenticação. |
| UC11 | Conferir cupom | Implementado sem login | Consulta, validação e prevenção de reutilização. |
| UC12 | Creditar moedas semestrais | Parcial | Crédito de 1.000, acumulação, histórico e unicidade; execução manual, sem agendamento. |
| UC13 | Enviar e-mail de notificação | Implementado (envio) | SMTP para transferência e resgate; entrega final não comprovada para todos os destinatários. |

## 3. Matriz de rastreabilidade — Histórias de usuário

| US | História | Situação Sprint 3 | Evidência / ressalva |
|---|---|---|---|
| US01 | Login | Não implementada | Ausência de autenticação e autorização. |
| US02 | Cadastro de aluno | Parcial | Cadastro completo, sem credenciais de acesso. |
| US03 | Editar/excluir meu cadastro | Parcial | CRUD, sem identificação do titular. |
| US04 | Notificação de moedas | Implementada (envio) | E-mail contém professor, quantidade e motivo; depende de SMTP. |
| US05 | Extrato do aluno | Implementada | Saldo e movimentos de recebimento e resgate. |
| US06 | Listar vantagens | Parcial | Listagem, descrição, empresa e custo; imagem opcional e sem autenticação. |
| US07 | Trocar moedas por vantagem | Implementada (sem login) | Resgate atômico e cupom; envio SMTP não garante entrega. |
| US08 | Enviar moedas | Parcial | Sem comprovação da exigência de mesma instituição. |
| US09 | Extrato do professor | Implementada | Saldo, envios e total distribuído. |
| US10 | Crédito semestral | Parcial | Crédito manual, acumulativo, histórico separado do extrato de transferências. |
| US11 | Professor pré-cadastrado | Parcial | Cadastro de professor existe; carga inicial institucional por seed/importação não confirmada. |
| US12 | Cadastro de empresa | Parcial | Cadastro sem login e senha. |
| US13 | Editar/excluir empresa | Parcial | CRUD sem restrição à empresa logada. |
| US14 | Cadastrar vantagem | Parcial | Imagem opcional e vínculo à empresa por ID, sem login. |
| US15 | Conferir cupom | Implementada (sem login) | Código validado e marcado como usado; sem autorização por empresa. |
| US16 | Instituições pré-cadastradas | Implementada | Listagem de instituições pelo banco; seed descrito na documentação. |

## 4. Modelo de classes — persistência efetiva

As especializações `Aluno`, `Professor` e `EmpresaParceira` usam `usuario_id` como PK/FK de `Usuario`. `Endereco` é 1:1 com `Usuario`; instituições vinculam alunos e professores. O modelo persistido não usa a hierarquia abstrata conceitual `Transacao`/`TransacaoEnvio`/`TransacaoResgate`: existem as tabelas concretas `transferencias_moedas` e `resgates_vantagens`.

| Entidade | Atributos-chave | Relacionamentos |
|---|---|---|
| Usuario | id, nome, email único, tipo, senha_hash opcional | endereço, aluno, professor, empresa |
| Aluno | usuario_id, cpf único, curso, saldo Decimal | instituição, resgates, transferências recebidas |
| Professor | usuario_id, cpf único, departamento, saldo Decimal | instituição, transferências enviadas, créditos |
| EmpresaParceira | usuario_id, cnpj único, telefone | vantagens e resgates |
| InstituicaoEnsino | id, nome, sigla | alunos e professores |
| TransferenciaMoedas | id, professor_id, aluno_id, quantidade, justificativa, criado_em | professor → aluno |
| Vantagem | id, empresa_id, nome, descrição, custo, imagem_url opcional, ativa | empresa e resgates |
| ResgateVantagem | id, aluno_id, vantagem_id, empresa_id, custo, codigo_cupom único, idempotency_key único, utilizado_em | aluno, vantagem e empresa |
| CreditoSemestral | id, professor_id, ano, semestre, quantidade, criado_em | professor; UNIQUE(professor_id, ano, semestre) |

## 5. Fluxos de negócio

**Transferência:** professor e aluno identificados por ID → validar saldo e quantidade → debitar professor e creditar aluno na mesma transação → registrar justificativa → `commit` → tentar enviar e-mail ao aluno. O código do serviço não verifica explicitamente que aluno e professor pertencem à mesma instituição.

**Resgate:** aluno seleciona vantagem → validar disponibilidade/saldo → débito e registro atômicos → gerar cupom único → `commit` → tentar enviar o mesmo código ao aluno e à empresa. A entrega real depende do provedor SMTP.

**Conferência de cupom:** consultar código → conferir se pertence à empresa informada e se não foi usado → validar → preencher `utilizado_em`; rejeitar código inválido/reutilizado. Não há autenticação da empresa.

**Crédito semestral:** professor inicia com 1.000 moedas; histórico `creditos_semestrais` registra o crédito inicial e os créditos posteriores. A rotina manual `POST /api/moedas/creditos-semestrais` adiciona 1.000 ao saldo atual apenas se não houver crédito para o par (ano, semestre). Não há scheduler automático.

## 6. Regras, limitações e evidências

- CPF/CNPJ/e-mail são únicos, com validações em schemas/services e restrições de persistência.
- Saldos usam `Numeric(14,2)`; crédito e débito são transacionais.
- Não existe login nem proteção das rotas administrativas; uso indicado apenas para demonstração controlada.
- Foto de vantagem é opcional no código, embora obrigatória no critério original da US14.
- O crédito semestral aparece em histórico próprio; não está mesclado ao extrato de transferências do professor.
- Os registros de crédito inicial de professores existentes são criados pela migração 0005 sem somar novamente o saldo.
- A evidência de teste de SMTP do aluno foi relatada na conversa; a caixa de entrada da empresa não foi verificada.
- Esta revisão é documental e estática: não foram executados testes, migrações nem chamadas à API durante sua produção.

## 7. Artefatos associados

- `Lab03S01-modelagem-atualizada.pdf`: versão histórica pós-Sprint 2, preservada.
- `Lab03S03-modelagem-atualizada.pdf`: síntese visual e matrizes da Sprint 3.
- `diagrama-classes-sprint3.mmd` e `diagrama-er-sprint3.mmd`: fontes editáveis dos diagramas.
- `RELATORIO-ALTERACOES-SPRINT3.md`: histórico de alterações e divergências.
