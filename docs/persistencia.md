# Camada de persistência

## Objetivo

A camada de persistência do Conquista armazena os cadastros finais de alunos, empresas parceiras, endereços e instituições. Ela mantém integridade referencial, unicidade dos documentos e atomicidade das operações de escrita.

O fluxo adotado é:

```text
FastAPI Router
    ↓
Service — regras e transação
    ↓
Repository — consultas e acesso aos dados
    ↓
SQLAlchemy — mapeamento ORM
    ↓
PostgreSQL no Neon
```

O diagrama editável está em [modelo-er.mmd](modelo-er.mmd). A relação com os modelos anteriores está documentada em [consistencia-uml.md](consistencia-uml.md).

## Tecnologias

| Responsabilidade | Tecnologia |
|---|---|
| Banco relacional | PostgreSQL hospedado no Neon |
| Driver | psycopg 3 |
| Mapeamento ORM | SQLAlchemy 2 |
| Migrações | Alembic |
| Configuração | Pydantic Settings e arquivo `.env` |
| Banco dos testes | SQLite isolado |

## Modelo relacional

### `usuarios`

Concentra os dados comuns às especializações de aluno e empresa.

| Campo | Tipo lógico | Regra |
|---|---|---|
| `id` | inteiro | chave primária |
| `nome` | texto de até 150 caracteres | obrigatório |
| `email` | texto de até 254 caracteres | obrigatório, único e indexado |
| `tipo` | texto | somente `ALUNO` ou `EMPRESA` |
| `senha_hash` | texto opcional | reservado para autenticação futura |
| `criado_em` | data e hora com fuso | preenchido pelo banco |
| `atualizado_em` | data e hora com fuso | atualizado pelo ORM |

### `enderecos`

Mantém uma relação um para um com `usuarios`. `usuario_id` é obrigatório e único. A chave estrangeira possui `ON DELETE CASCADE`, portanto a remoção do usuário também remove seu endereço.

CEP é armazenado somente com oito dígitos e UF com duas letras maiúsculas. A normalização ocorre nos schemas Pydantic antes da persistência.

### `instituicoes_ensino`

Armazena as instituições disponíveis no cadastro do aluno. Nome e sigla são únicos. A instituição é referenciada por `alunos.instituicao_id` com `ON DELETE RESTRICT`, impedindo a exclusão de uma instituição que ainda possua alunos vinculados.

### `alunos`

Especializa `usuarios` por meio de `usuario_id`, que funciona simultaneamente como chave primária e chave estrangeira.

| Campo | Regra |
|---|---|
| `usuario_id` | PK e FK para `usuarios.id`, com cascata |
| `cpf` | 11 dígitos, obrigatório, único e indexado |
| `rg` | obrigatório |
| `curso` | obrigatório |
| `instituicao_id` | FK obrigatória para `instituicoes_ensino.id` |
| `saldo` | `NUMERIC(14,2)`, obrigatório, padrão `0.00` |

CPF e saldo não aparecem no schema de atualização. Assim, a API não permite modificar esses campos pelo CRUD cadastral.

### `empresas_parceiras`

Também especializa `usuarios` por PK/FK compartilhada. CNPJ é obrigatório, único e indexado. O schema de atualização não contém CNPJ, mantendo o documento imutável após o cadastro.

## Mapeamento ORM

As entidades ficam em `backend/app/models/entities.py` e usam a API tipada do SQLAlchemy 2:

- `Mapped` declara o tipo Python de cada atributo;
- `mapped_column` configura colunas, chaves e restrições;
- `relationship` define navegação bidirecional;
- `back_populates` mantém os dois lados sincronizados;
- `cascade="all, delete-orphan"` remove endereço e especialização junto ao usuário;
- `CheckConstraint` restringe o tipo de usuário;
- `Numeric(14, 2)` evita erros de ponto flutuante no saldo.

`Usuario` funciona como agregado de persistência: no cadastro, o service monta o usuário com endereço e sua especialização. O SQLAlchemy ordena os `INSERTs` conforme as dependências de chave estrangeira.

## Repositories e consultas

`UsuarioRepository` encapsula:

- verificação de e-mail existente;
- listagem e busca de alunos;
- listagem e busca de empresas;
- consulta detalhada por identificador;
- obtenção de instituição;
- contagem de usuários por tipo para o dashboard.

As listagens usam `select`, ordenação no banco e filtros `ILIKE`. Documentos são pesquisados na forma numérica. `selectinload` antecipa endereço, especialização e instituição, evitando consultas repetidas durante a serialização da resposta.

O dashboard executa `COUNT` no PostgreSQL em vez de transferir todos os registros ao frontend.

### Aderência ao padrão Repository

A implementação segue predominantemente o Repository, mas ainda possui uma ressalva: os services consultam CPF/CNPJ e executam `add` e `delete` diretamente pela sessão SQLAlchemy. Uma futura refatoração pode mover esses comandos para o repository sem alterar as regras ou os contratos HTTP.

O controle de `commit` e `rollback` deve permanecer no service, pois uma operação de negócio pode envolver mais de um comando de persistência.

## Sessões

O módulo `backend/app/database/session.py` cria o engine e a fábrica de sessões:

- `pool_pre_ping=True` verifica conexões antes do uso e reduz falhas por conexões expiradas;
- `autoflush=False` evita envio implícito antes do momento controlado pela aplicação;
- `expire_on_commit=False` mantém os objetos disponíveis para montar a resposta após o commit;
- `check_same_thread=False` é aplicado somente ao SQLite de desenvolvimento/teste.

A dependency `get_db` abre uma sessão por requisição e sempre executa `close()` no bloco `finally`. A sessão não é compartilhada entre requisições.

## Transações e rollback

Cada criação, atualização ou exclusão é tratada como uma unidade atômica:

1. Pydantic valida e normaliza o payload.
2. O service verifica regras e duplicidades conhecidas.
3. As alterações são adicionadas à sessão.
4. O service executa `commit` uma única vez.
5. Em caso de `IntegrityError`, o service executa `rollback` e gera `ConflictError`.
6. O handler global converte o conflito em HTTP `409` sem expor SQL ou credenciais.

As verificações prévias fornecem mensagens específicas, mas as restrições do PostgreSQL continuam sendo a última proteção contra requisições concorrentes.

## Integridade e normalização

A persistência é protegida em três níveis:

| Nível | Exemplos |
|---|---|
| Pydantic | CPF/CNPJ, e-mail, CEP, UF e campos obrigatórios |
| Service | instituição existente, documentos/e-mail duplicados e campos imutáveis |
| PostgreSQL | `UNIQUE`, `NOT NULL`, `CHECK`, PK e FK |

CPF, CNPJ e CEP são persistidos somente com dígitos. E-mails são convertidos para letras minúsculas. Nomes, RG, curso e telefone têm espaços externos removidos.

## Migrações Alembic

O Alembic usa `Base.metadata` como fonte dos modelos e lê a mesma `DATABASE_URL` da aplicação. A configuração oferece execução online e offline e habilita `compare_type=True` para detectar alterações de tipos.

A revisão `20261026_0001_sprint2.py` cria:

- `instituicoes_ensino`;
- `usuarios`;
- `enderecos`;
- `alunos`;
- `empresas_parceiras`;
- índices, unicidades, checks e chaves estrangeiras.

As alterações da Sprint 3 afetam validações, consultas e documentação, sem mudança do schema. Por isso, nenhuma nova revisão Alembic foi necessária.

Comandos locais usuais:

```powershell
Set-Location .\backend
alembic current
alembic upgrade head
alembic history
```

Antes de aplicar uma migração em qualquer ambiente remoto, a equipe deve revisar o SQL, testar em banco descartável e manter um plano de recuperação. Esta entrega não executou migrações no Neon.

## Seed de instituições

`backend/app/database/seed.py` cadastra PUC Minas, UFMG e CEFET-MG. O processo é idempotente: consulta as siglas existentes e insere apenas as ausentes.

O seed não atualiza nem remove instituições existentes. Ainda assim, sua execução no Neon deve ocorrer somente em ambiente autorizado.

## PostgreSQL no Neon

A conexão de produção acadêmica usa uma URL semelhante a:

```dotenv
DATABASE_URL=postgresql+psycopg://usuario:senha@host/neondb?sslmode=require
```

Regras de configuração:

- manter `sslmode=require`;
- nunca versionar o `.env`;
- usar `.env.example` apenas como modelo sem segredos;
- restringir as origens de CORS;
- não exibir ou registrar a URL completa do banco;
- usar credenciais diferentes por ambiente quando possível.

O arquivo `.env` da raiz está ignorado pelo Git. O frontend nunca recebe a `DATABASE_URL`; ele conhece apenas a URL HTTP da API.

## Persistência nos testes

Os testes backend substituem a dependency `get_db` por uma sessão SQLite própria. Antes de cada teste, as tabelas são recriadas e uma instituição é inserida. Ao final, tabelas e arquivo temporário são removidos.

Essa estratégia valida persistência após criação e atualização, exclusão, duplicidades, instituição inexistente, campos protegidos e respostas para registros inexistentes sem acessar o Neon.

SQLite não substitui uma validação de compatibilidade com PostgreSQL para recursos específicos do banco, mas é adequado à suíte rápida atual. Migrações devem ser verificadas separadamente em PostgreSQL descartável antes de uso remoto.

## Extensão do fluxo de moedas

As migrações incrementais preservam todas as tabelas e IDs anteriores:

- `20261109_0002` adiciona `professores` e `transferencias_moedas` e amplia o tipo de usuário;
- `20261109_0003` adiciona `vantagens` e `resgates_vantagens`.

`professores.saldo` inicia em `1000.00` e possui check não negativo. Transferências exigem quantidade positiva. Vantagens exigem custo positivo. Resgates guardam o custo histórico, cupom único e chave de idempotência única.

Os débitos de professor e aluno são condicionais e atômicos. A atualização somente ocorre quando o saldo atual é suficiente, protegendo contra concorrência sem depender de cálculos realizados apenas em memória.

O modelo completo desta extensão está em [modelo-er-moedas.mmd](modelo-er-moedas.mmd). O modelo cadastral anterior foi preservado em [modelo-er.mmd](modelo-er.mmd).

## Operação segura

### Permitido no desenvolvimento local

- executar testes com SQLite;
- criar um banco PostgreSQL descartável;
- inspecionar SQL de migração;
- aplicar seed em banco local;
- testar CRUDs com dados fictícios.

### Exige autorização explícita

- executar `alembic upgrade` no Neon;
- executar seed no Neon;
- inserir, atualizar ou excluir dados remotos;
- alterar credenciais ou configurações do projeto Neon;
- executar qualquer operação destrutiva ou de limpeza.

Nenhuma operação de escrita, seed ou migração foi executada no banco Neon durante esta Sprint 3.
