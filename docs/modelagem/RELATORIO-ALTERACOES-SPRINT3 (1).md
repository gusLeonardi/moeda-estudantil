# Relatório de alterações — Sprint 3

**Base:** ZIP do repositório recebido em 09/11/2026. Revisão estática, sem executar o código.

## Preservado
- `Lab03S01-modelagem-atualizada.pdf` mantido como registro histórico pós-Sprint 2.
- Identificadores UC01–UC13 e US01–US16 preservados.
- A arquitetura React/FastAPI/Services/Repositories/SQLAlchemy/PostgreSQL permanece.

## Atualizado
- Criado `Lab03S03-modelagem-atualizada.md` com rastreabilidade de 13 UCs e 16 USs.
- Criado `Lab03S03-modelagem-atualizada.pdf` como síntese de entrega.
- Criados diagramas Mermaid de classes e ER para a implementação da Sprint 3.
- Incluídos Professor, TransferenciaMoedas, Vantagem, ResgateVantagem e CreditoSemestral.
- Registrados SMTP, resgates e conferência de cupons, saldo acumulativo e unicidade do crédito semestral.

## Divergências dos critérios originais
1. Não existe autenticação/autorização; recursos de 'meu cadastro' ou 'empresa logada' não têm isolamento.
2. A transferência não demonstra verificação de instituição igual para professor e aluno.
3. A foto da vantagem é opcional.
4. Crédito semestral é acionado manualmente; histórico é separado do extrato de transferências.
5. Pré-cadastro por importação/seed de professores não foi confirmado.
6. Envio de e-mail implementado não equivale à confirmação de entrega para todos os destinatários.

## Nota
A classificação 'parcial' significa que parte do critério original permanece sem implementação, mesmo quando o fluxo principal já funciona.
