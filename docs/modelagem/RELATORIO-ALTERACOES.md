# Relatório de alterações — Lab03S01: Modelagem

Documento de origem: `Lab03S01-modelagem.pdf` (Sprint 1, recuperado do commit `5d253b4^`; o arquivo original não foi alterado).
Documento gerado: `Lab03S01-modelagem-atualizada.pdf` (13 páginas, diagramas vetoriais).
Base de conferência: código do repositório no commit `5d253b4`, lido (não executado).

## Elementos modificados

| Elemento | Alteração | Motivo |
|---|---|---|
| Diagrama de componentes | Redesenhado em notação UML (componentes, interface REST com bola e soquete, dependências). Jinja2 substituído por React + TypeScript; incluídos Axios, Pydantic, Alembic, PostgreSQL no Neon e Uvicorn. Componentes marcados como implementados ou previstos. | O código usa React, não templates Jinja2. |
| Descrição dos componentes | Nova tabela com situação de cada componente. Removida a menção a Jinja2 como View. | Mesmo motivo. |
| Diagrama de classes | Redesenhado com legenda de situação. `nome` movido para `Usuario`; `Endereco` ligado a `Usuario` (composição 1–1); `telefone` em `EmpresaParceira` e `sigla` em `InstituicaoEnsino` acrescentados; restrições `{unique}` indicadas. | Conferência com `entities.py`. |
| Diagrama de casos de uso | Redesenhado com a mesma lista de atores e UC01–UC13; UC07 passa a incluir UC01; UC03, UC04, UC05 e UC02 destacados como parciais. | Pré-condição "autenticado" de UC07 já existia na Sprint 1. |
| Matriz de rastreabilidade | Ganhou as colunas Componentes e Situação. | Pedido da revisão. |
| Ator secundário | Renomeado de "Sistema (Scheduler/E-mail)" para "Sistema (agendamento e notificações)". | Nome pedido na revisão; responsabilidade inalterada. |

## Elementos preservados

- Capa com disciplina, professora e os quatro nomes dos integrantes, sem alteração.
- Atores e suas descrições.
- UC01–UC13 e todos os casos de uso das funcionalidades futuras.
- As 16 histórias de usuário (US01–US16), com texto, prioridade e critérios de aceite idênticos aos da Sprint 1.
- Identificadores de requisitos, casos de uso e histórias.
- Classes conceituais da Sprint 1 (Professor, Vantagem, Transacao, TransacaoEnvio, TransacaoResgate, enums), com atributos e métodos originais.
- Decisões de modelagem e regras de saldo do documento original.

## Elementos acrescentados

- Seção "Sobre esta versão", com convenção de situação (Implementado, Implementado*, Parcial, Pendente).
- Coluna de situação na tabela de casos de uso e descrição de UC03, UC05 e UC13, que existiam no diagrama e na matriz, mas não na tabela.
- Tabela de acompanhamento das 16 histórias, com justificativa por critério.
- Regras de saldo protegido e de unicidade (e-mail, CPF, CNPJ) nas decisões de modelagem.
- Tabela "Modelo conceitual × entidades persistidas na Sprint 2".
- Seção "Evolução da Arquitetura — Sprint 1 para Sprint 2", com os nove itens pedidos.
- Linhas de instituições pré-cadastradas (US16) e listagem de vantagens (UC07/US06) na matriz de rastreabilidade.
- Conclusão sobre o alinhamento entre modelagem e implementação.

## Classificação das histórias

| História | Situação | Observação |
|---|---|---|
| US16 | Implementado | Endpoint `/api/instituicoes` e seed. |
| US03, US13 | Implementado* | Critérios atendidos, mas sem restrição ao "meu" cadastro, pois não há login. |
| US02, US12 | Parcial | Falta definir login e senha. |
| Demais (US01, US04–US11, US14, US15) | Pendente | Dependem de autenticação, professores, transações, vantagens, e-mail ou agendamento. |

Esta classificação é mais conservadora que o rascunho do pedido para US03: a história fala em "meus dados", o que pressupõe usuário autenticado.

## Divergências entre modelo e código (decisão da Sprint 3)

1. `login` existe no modelo conceitual, mas não no código; o e-mail é o único identificador.
2. `saldo` é inteiro no modelo conceitual e `Numeric(14,2)` no banco.
3. `usuarios.tipo` aceita apenas ALUNO e EMPRESA; o enum `Perfil` prevê PROFESSOR.
4. `Endereco` ficou associado a `Usuario`; na Sprint 1 estava ligado ao aluno.
5. A UC13 e o `UC07 → UC01` são esclarecimentos de documentação, não requisitos novos.

## Limitações

- O PlantUML não está instalado nesta máquina e o download do jar foi bloqueado. Por isso os arquivos `fonte/plantuml/*.puml` **não foram renderizados nem validados**. Os diagramas do PDF foram desenhados diretamente por `fonte/gerar_pdf.py` (reportlab) e são a fonte de verdade visual.
- O alinhamento foi conferido por leitura do código, sem executar os testes.
- O gerador usa fontes do macOS (`/System/Library/Fonts/Supplemental`).

## Como regenerar

```bash
python3 -m venv .venv-doc && .venv-doc/bin/pip install reportlab
.venv-doc/bin/python docs/modelagem/fonte/gerar_pdf.py docs/modelagem/Lab03S01-modelagem-atualizada.pdf
```
