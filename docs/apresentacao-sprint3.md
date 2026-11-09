# Apresentação da Sprint 3 — Conquista

## Distribuição dos 20 minutos

| Intervalo | Duração | Conteúdo |
|---|---:|---|
| 00:00–01:00 | 1 min | Introdução ao Conquista e objetivo da Sprint 3 |
| 01:00–02:30 | 1 min 30 s | Tecnologias utilizadas |
| 02:30–04:30 | 2 min | Arquitetura em camadas e MVC adaptado |
| 04:30–07:30 | 3 min | Tutorial: Pydantic, Service, Repository, SQLAlchemy e Alembic |
| 07:30–13:30 | 6 min | Demonstração prática dos CRUDs |
| 13:30–15:00 | 1 min 30 s | Persistência e integração segura com Neon |
| 15:00–17:00 | 2 min | Testes, validações e build |
| 17:00–18:30 | 1 min 30 s | Recapitulação do fluxo completo de cadastro |
| 18:30–19:00 | 30 s | Conclusão |
| 19:00–20:00 | 1 min | Perguntas e margem técnica |
| **Total** | **20 min** | |

As seções detalhadas abaixo funcionam como material de apoio. Durante a fala, seguir esta linha do tempo e selecionar apenas os exemplos indicados.

## Tutorial curto das tecnologias — 04:30 a 07:30

Usar o cadastro de aluno como fio condutor:

1. **Pydantic — 30 segundos:** abrir `AlunoCreate` e mostrar tipos, e-mail e validação do CPF.
2. **Service — 30 segundos:** mostrar `AlunoService.create` verificando instituição e duplicidades.
3. **Repository — 30 segundos:** mostrar a consulta da instituição ou a verificação de e-mail.
4. **SQLAlchemy — 45 segundos:** mostrar `Usuario`, `Aluno`, PK/FK e `relationship`.
5. **Sessão e transação — 30 segundos:** mostrar `commit`, `IntegrityError` e `rollback`.
6. **Alembic — 15 segundos:** mostrar a revisão que cria tabelas e restrições.

Não explicar cada linha. Destacar a responsabilidade de cada tecnologia e avançar para a próxima camada.

## Demonstração prática — 07:30 a 13:30

### Alunos — 4 minutos

1. Mostrar a listagem e iniciar um novo cadastro.
2. Selecionar uma instituição pré-cadastrada.
3. Demonstrar uma validação de CPF ou e-mail.
4. Concluir um cadastro válido.
5. Buscar e abrir os detalhes.
6. Editar um campo permitido e mostrar CPF/saldo protegidos.
7. Excluir usando o diálogo de confirmação.

### Empresas — 2 minutos

1. Cadastrar uma empresa fictícia.
2. Demonstrar CNPJ inválido ou duplicado.
3. Buscar e abrir os detalhes.
4. Mostrar o CNPJ imutável na edição.
5. Excluir com confirmação.

Se o tempo estiver terminando, omitir a exclusão da empresa e mostrar apenas a confirmação sem concluir a operação.

## Recapitulação do fluxo — 17:00 a 18:30

```text
Formulário React
    ↓ Zod
Axios envia JSON
    ↓
Router FastAPI
    ↓ Pydantic
Service aplica regras
    ↓
Repository consulta dados
    ↓
SQLAlchemy abre a transação
    ↓
PostgreSQL garante integridade
    ↓
Resposta HTTP atualiza a interface
```

Usar [sequencia-cadastro-aluno.mmd](sequencia-cadastro-aluno.mmd) como apoio visual.

## 1. Introdução ao Conquista

### Objetivo da seção

Apresentar o problema, a proposta do sistema e o recorte entregue na Sprint 3.

### Sugestão de fala

> O Conquista é um Sistema de Moeda Estudantil desenvolvido na disciplina Projeto de Software da PUC Minas. A proposta é criar um ambiente de reconhecimento acadêmico no qual, em etapas futuras, professores poderão conceder moedas aos alunos e empresas parceiras poderão oferecer benefícios.
>
> Nesta Sprint 3, concentramos o trabalho na base cadastral do sistema. Finalizamos os CRUDs de alunos e empresas parceiras, consolidamos a arquitetura em camadas e documentamos a persistência com SQLAlchemy, Alembic e PostgreSQL no Neon.
>
> O escopo desta entrega não inclui professores, autenticação, transações, distribuição de moedas, vantagens ou resgates. Esses recursos permanecem previstos para evolução futura e dependem de autorização para implementação.

### Pontos para o slide

- sistema acadêmico de reconhecimento estudantil;
- desenvolvido para a disciplina Projeto de Software da PUC Minas;
- frontend React integrado a uma API FastAPI;
- Sprint 3 focada nos CRUDs finais, arquitetura e persistência;
- evolução futura sem funcionalidades fictícias nesta entrega.

### Apoio visual

Usar a tela inicial do sistema ou o título do projeto acompanhado do fluxo resumido:

```text
React → FastAPI → Services → Repositories → SQLAlchemy → PostgreSQL
```

### Tempo sugerido

1 minuto.

## 2. Visão geral da arquitetura

### Objetivo da seção

Mostrar como o sistema está dividido, como uma requisição atravessa as camadas e como a implementação adapta o padrão MVC.

### Sugestão de fala

> A arquitetura separa o frontend React da API FastAPI. O navegador não acessa diretamente o banco de dados. Toda operação passa pela API usando HTTP e JSON.
>
> Os Routers funcionam como Controllers: recebem a requisição, aplicam os schemas Pydantic e delegam a operação. Os Services concentram regras de negócio e coordenam as transações. Os Repositories encapsulam as consultas, enquanto o SQLAlchemy mapeia as entidades para o PostgreSQL.
>
> Essa organização adapta o MVC da modelagem original. A View é o cliente React, o Controller corresponde aos Routers FastAPI e o Model reúne Services, Repositories, entidades SQLAlchemy e banco de dados.

### Fluxo principal

```text
React + TypeScript
        ↓ HTTP / JSON
FastAPI Routers + Pydantic
        ↓
Services
        ↓
Repositories
        ↓
SQLAlchemy
        ↓
PostgreSQL no Neon
```

### Responsabilidades

| Camada | Responsabilidade |
|---|---|
| React | interface, navegação, formulários e feedback |
| Routers | protocolo HTTP, dependências e status de resposta |
| Pydantic | validação e serialização dos contratos |
| Services | regras de negócio e delimitação das transações |
| Repositories | consultas e operações de acesso aos dados |
| SQLAlchemy | mapeamento ORM e sessões |
| PostgreSQL | integridade e armazenamento persistente |
| Alembic | evolução versionada do schema |

### Adaptação do MVC

| MVC | Conquista |
|---|---|
| View | frontend React |
| Controller | Routers FastAPI |
| Model | Services, Repositories, SQLAlchemy e PostgreSQL |

### Decisões importantes

- frontend e backend podem evoluir de forma independente;
- regras não ficam nos componentes React nem nos Routers;
- o banco não é acessado diretamente pelo navegador;
- Pydantic e Zod validam fronteiras diferentes;
- restrições do PostgreSQL permanecem como proteção definitiva;
- autenticação e operações com moedas estão fora do escopo atual.

### Apoio visual

Exibir [arquitetura-camadas.mmd](arquitetura-camadas.mmd) e, se houver tempo, [componentes.mmd](componentes.mmd).

### Tempo sugerido

2 minutos.

## 3. Explicação do Repository/DAO

### Objetivo da seção

Explicar por que o acesso aos dados fica separado dos Routers e das regras de negócio.

### Sugestão de fala

> O Repository, também chamado de DAO neste contexto, encapsula as consultas e operações de acesso aos dados. Ele funciona como uma fronteira entre os Services e o SQLAlchemy.
>
> O Service informa o que precisa, como localizar um aluno, verificar um e-mail ou listar empresas. O Repository define como essa consulta será executada. Assim, detalhes como joins, filtros e carregamento de relacionamentos não ficam espalhados pelas regras de negócio.
>
> No Conquista, o `UsuarioRepository` concentra as consultas dos dois tipos de usuário e o `BaseRepository` oferece operações genéricas. A implementação atual segue esse padrão predominantemente, embora algumas verificações de documento e comandos de inclusão ou exclusão ainda utilizem a sessão diretamente nos Services.

### Fluxo de responsabilidades

```text
Router
  recebe HTTP
      ↓
Service
  aplica regras e coordena a transação
      ↓
Repository
  constrói consultas e acessa a sessão
      ↓
SQLAlchemy
  traduz a operação para SQL
      ↓
PostgreSQL
```

### Operações do `UsuarioRepository`

- verificar se um e-mail já existe;
- listar alunos com busca e ordenação;
- consultar um aluno por identificador;
- listar empresas com busca e ordenação;
- consultar uma empresa por identificador;
- localizar uma instituição;
- contar usuários por tipo para o dashboard.

### Exemplo de verificação de e-mail

```python
def email_exists(self, email: str, except_id: int | None = None) -> bool:
    stmt = select(Usuario.id).where(Usuario.email == email.lower())
    if except_id is not None:
        stmt = stmt.where(Usuario.id != except_id)
    return self.db.scalar(stmt) is not None
```

Durante a edição, `except_id` permite ignorar o próprio usuário e detectar somente outro cadastro com o mesmo e-mail.

### Exemplo de consumo pelo Service

```python
if self.repo.email_exists(str(data.email), entity_id):
    raise ConflictError("E-mail já cadastrado")
```

O Service conhece a regra de unicidade e a mensagem de negócio, mas não precisa conhecer a consulta SQLAlchemy usada para encontrar o e-mail.

### Busca de alunos

O Repository monta uma consulta que pode filtrar por:

- nome;
- e-mail;
- CPF;
- curso;
- nome ou sigla da instituição.

Ele também ordena por nome e antecipa endereço e instituição com `selectinload`.

### Contagem do dashboard

```python
def count_by_type(self, user_type: str) -> int:
    return self.db.scalar(
        select(func.count(Usuario.id))
        .where(Usuario.tipo == user_type)
    ) or 0
```

Essa consulta retorna somente o total necessário, evitando transferir registros completos para o frontend.

### Benefícios

- consultas centralizadas;
- menor acoplamento entre regra de negócio e banco;
- Routers sem código de persistência;
- otimizações sem alteração do contrato HTTP;
- maior facilidade para testar Services com dependências controladas;
- reutilização das consultas entre operações.

### Ressalva da implementação atual

Os Services ainda consultam CPF/CNPJ e executam `add` e `delete` diretamente pela sessão. Isso representa uma aderência parcial ao Repository proposto no UML.

Uma refatoração futura pode mover essas operações para o Repository. `commit` e `rollback` devem continuar nos Services, pois eles delimitam a transação completa da regra de negócio.

### Repository não substitui o Service

| Repository | Service |
|---|---|
| sabe como consultar ou persistir | sabe quando a operação é permitida |
| trabalha com SQLAlchemy e sessão | aplica as regras de negócio |
| não conhece HTTP | traduz situações em erros do domínio |
| não decide o fluxo da interface | coordena a transação completa |

### Apoio visual

Exibir [componentes.mmd](componentes.mmd) e destacar somente o trecho `Service → Repository → SQLAlchemy`.

### Tempo sugerido

2 minutos.

## 4. Tecnologias utilizadas

### Objetivo da seção

Apresentar a stack do Conquista e explicar a função de cada tecnologia na solução.

### Sugestão de fala

> O Conquista possui um frontend React independente e uma API REST construída com FastAPI. TypeScript fornece tipagem no cliente, enquanto Pydantic valida os contratos recebidos pelo servidor.
>
> No frontend, utilizamos Vite para desenvolvimento e build, Tailwind CSS para estilização, React Router para navegação, React Hook Form com Zod para formulários e Axios para a comunicação HTTP.
>
> No backend, SQLAlchemy realiza o mapeamento objeto-relacional, Alembic versiona a estrutura do banco e psycopg conecta a aplicação ao PostgreSQL hospedado no Neon. Os testes usam pytest no backend e Vitest com Testing Library no frontend.

### Frontend

| Tecnologia | Responsabilidade |
|---|---|
| React | construção das páginas e componentes |
| TypeScript | tipagem dos dados e contratos da API |
| Vite | servidor de desenvolvimento e build de produção |
| Tailwind CSS | identidade visual e responsividade |
| React Router | navegação entre dashboard, listas, formulários e detalhes |
| React Hook Form | estado e envio dos formulários |
| Zod | validação dos dados antes da chamada à API |
| Axios | comunicação HTTP com o FastAPI |
| Lucide React | ícones da interface |

### Backend

| Tecnologia | Responsabilidade |
|---|---|
| Python | linguagem do servidor |
| FastAPI | API REST, rotas e injeção de dependências |
| Pydantic | validação e serialização dos contratos HTTP |
| SQLAlchemy 2 | mapeamento ORM, consultas e sessões |
| Alembic | controle de versão do schema |
| psycopg 3 | driver de conexão com PostgreSQL |
| Uvicorn | servidor ASGI da aplicação |

### Banco e qualidade

| Tecnologia | Responsabilidade |
|---|---|
| PostgreSQL no Neon | persistência relacional da aplicação |
| SQLite | banco isolado usado somente nos testes backend |
| pytest | testes automatizados da API e persistência |
| Vitest | testes automatizados do frontend |
| Testing Library | suporte para testes de comportamento da interface |

### Apoio visual

```text
React + TypeScript + Zod
          ↓ Axios / JSON
FastAPI + Pydantic
          ↓
Services + Repositories
          ↓
SQLAlchemy + psycopg
          ↓
PostgreSQL no Neon
```

Evitar mostrar credenciais, conteúdo do `.env` real ou a URL privada do banco.

### Tempo sugerido

2 minutos.

## 5. Objetivo do projeto

### Objetivo da seção

Explicar o resultado que o Conquista pretende alcançar e diferenciar a visão completa do sistema da entrega atual.

### Sugestão de fala

> O objetivo do Conquista é oferecer uma plataforma para reconhecer a participação e o desempenho acadêmico dos estudantes por meio de uma moeda virtual. No modelo completo, professores poderão conceder moedas aos alunos, e empresas parceiras poderão disponibilizar produtos, descontos ou outros benefícios.
>
> Para que esses fluxos futuros funcionem com segurança, o sistema precisa primeiro manter uma base cadastral consistente. Por isso, a Sprint 3 finaliza o cadastro de alunos e empresas, garante vínculos corretos com instituições, protege documentos e saldo e estabelece uma camada de persistência confiável.
>
> A entrega também demonstra como o frontend, a API e o banco de dados se comunicam, deixando a arquitetura preparada para evoluções posteriores sem implementar antecipadamente funcionalidades fora do escopo.

### Objetivo geral

Construir uma aplicação web que conecte a comunidade acadêmica e empresas parceiras em um ecossistema de reconhecimento estudantil.

### Objetivos da Sprint 3

- finalizar os CRUDs de alunos e empresas parceiras;
- validar CPF, CNPJ, e-mail e campos obrigatórios;
- proteger documentos imutáveis e o saldo do aluno;
- consolidar a integração entre React, FastAPI e PostgreSQL;
- documentar arquitetura, persistência e modelos;
- demonstrar o protótipo e as tecnologias adotadas.

### Limite da entrega

Professores, autenticação, transações, moedas, vantagens e resgates não fazem parte desta Sprint 3.

### Apoio visual

Apresentar dois níveis de objetivo:

```text
Visão do produto
Reconhecimento acadêmico por moeda estudantil

Entrega da Sprint 3
Base cadastral confiável de alunos e empresas
```

### Tempo sugerido

1 minuto.

## 6. MVC adaptado ao React e FastAPI

### Objetivo da seção

Relacionar a arquitetura implementada ao padrão MVC apresentado na modelagem acadêmica.

### Sugestão de fala

> No MVC tradicional, o servidor pode construir a View usando templates. O diagrama original do projeto mencionava Jinja2, mas a stack adotada separa completamente o frontend e o backend.
>
> No Conquista, a View é implementada em React. Ela mostra dados, captura entradas e apresenta feedback ao usuário. Os Routers do FastAPI exercem o papel de Controller, pois recebem as requisições, validam os contratos e selecionam o fluxo adequado.
>
> O Model não corresponde apenas às classes do banco. Ele reúne as entidades SQLAlchemy, os Repositories que acessam os dados e os Services que aplicam as regras de negócio. Assim, a divisão de responsabilidades do MVC permanece preservada mesmo com o React executando separadamente no navegador.

### Mapeamento

| Elemento MVC | Implementação no Conquista | Exemplos |
|---|---|---|
| View | React | páginas, componentes, formulários e mensagens |
| Controller | FastAPI Routers | endpoints de alunos, empresas e instituições |
| Model | domínio e persistência | Services, Repositories, SQLAlchemy e PostgreSQL |

### Comunicação entre as partes

```text
View React
    ↓ requisição HTTP com JSON
Controller FastAPI
    ↓ chamada de operação
Model: Service + Repository + ORM
    ↓ resultado
Controller serializa a resposta
    ↓ JSON
View atualiza a interface
```

### Exemplo do projeto

No cadastro de aluno:

1. `AlunoForm.tsx` captura e valida os dados na View.
2. `POST /api/alunos` recebe a requisição no Controller.
3. `AlunoService.create` verifica instituição e duplicidades.
4. `UsuarioRepository` consulta os dados necessários.
5. SQLAlchemy persiste `Usuario`, `Endereco` e `Aluno`.
6. O Router devolve `AlunoResponse` com HTTP `201`.
7. React redireciona para a listagem e informa o resultado.

### Diferença em relação ao UML inicial

```text
UML inicial: View com templates Jinja2 no servidor
Implementação: View React independente no navegador
```

A alteração afeta a tecnologia da View, não a responsabilidade arquitetural. O backend oferece uma API REST em vez de renderizar HTML.

### Cuidados arquiteturais

- componentes React não acessam o banco;
- Routers não concentram regras de negócio;
- Services não dependem de elementos da interface;
- Repositories não conhecem HTTP ou componentes React;
- respostas usam schemas públicos, não objetos internos do banco diretamente.

### Apoio visual

Exibir o quadro de mapeamento MVC e o arquivo [arquitetura-camadas.mmd](arquitetura-camadas.mmd).

### Tempo sugerido

2 minutos.

## 7. Demonstração dos CRUDs

### Objetivo da seção

Comprovar o funcionamento integrado do frontend, API e banco por meio dos fluxos de alunos e empresas parceiras.

### Preparação antes da apresentação

- iniciar backend e frontend em terminais separados;
- usar banco local ou instância descartável autorizada;
- executar o seed local para disponibilizar as instituições;
- manter Swagger aberto em uma aba de apoio;
- preparar dados completamente fictícios;
- confirmar que nenhuma credencial ou URL privada aparece na tela;
- manter um cadastro fictício pronto caso seja necessário reduzir o tempo.

### Sugestão de fala

> Agora vamos demonstrar os CRUDs finalizados na Sprint 3. A interface React envia as operações para a API FastAPI, que aplica as validações e persiste os dados por meio do SQLAlchemy.
>
> Primeiro mostraremos o fluxo de alunos, incluindo instituição, validação de CPF, proteção do saldo e confirmação de exclusão. Em seguida, repetiremos os principais passos para uma empresa parceira, destacando a validação e a imutabilidade do CNPJ.

### Roteiro do CRUD de alunos

#### 1. Listagem e estado inicial

1. Abrir **Alunos** pelo menu lateral.
2. Mostrar o carregamento e a listagem existente.
3. Explicar o estado vazio caso não existam registros.
4. Destacar ações de detalhes, edição e exclusão.

Resultado esperado: a página consulta `GET /api/alunos` e apresenta os registros retornados.

#### 2. Cadastro válido

1. Selecionar **Novo aluno**.
2. Preencher dados fictícios.
3. Escolher uma instituição pré-cadastrada.
4. Salvar o formulário.

Exemplo fictício:

```text
Nome: Aluno Demonstração
E-mail: aluno.demo@example.com
CPF de teste válido: 529.982.247-25
RG: MG-DEMO-001
Curso: Engenharia de Software
Instituição: PUC Minas
Endereço: dados fictícios para demonstração local
```

Resultado esperado: `POST /api/alunos` retorna HTTP `201`, o saldo começa em `0.00` e o aluno aparece na listagem.

#### 3. Validações e duplicidade

1. Tentar informar um CPF com dígitos verificadores inválidos.
2. Mostrar a mensagem do formulário.
3. Tentar reutilizar o CPF ou e-mail do cadastro anterior.

Resultado esperado: dados inválidos são bloqueados; duplicidades retornam HTTP `409` com mensagem controlada.

#### 4. Busca e detalhes

1. Buscar pelo nome fictício.
2. Repetir com CPF, curso ou instituição.
3. Abrir os detalhes do aluno.
4. Mostrar dados acadêmicos, instituição, endereço e saldo.

Resultado esperado: `GET /api/alunos?busca=...` filtra no banco e `GET /api/alunos/{id}` retorna o cadastro completo.

#### 5. Edição e campos protegidos

1. Abrir a edição.
2. Mostrar que o CPF está desabilitado.
3. Alterar curso, e-mail ou endereço.
4. Salvar e retornar aos detalhes.
5. Confirmar que o saldo não aparece como campo editável.

Resultado esperado: `PUT /api/alunos/{id}` modifica somente os campos permitidos, preservando CPF e saldo.

#### 6. Exclusão

1. Acionar a exclusão na listagem.
2. Mostrar o diálogo de confirmação.
3. Cancelar uma vez para demonstrar proteção.
4. Abrir novamente e confirmar.

Resultado esperado: `DELETE /api/alunos/{id}` retorna HTTP `204` e o registro deixa de aparecer.

### Roteiro do CRUD de empresas

#### 1. Cadastro

1. Abrir **Empresas**.
2. Selecionar **Nova empresa**.
3. Preencher dados fictícios e salvar.

Exemplo fictício:

```text
Nome: Empresa Demonstração
E-mail: empresa.demo@example.com
CNPJ de teste válido: 11.222.333/0001-81
Telefone: (31) 3333-4444
Endereço: dados fictícios para demonstração local
```

Resultado esperado: `POST /api/empresas` retorna HTTP `201`.

#### 2. Busca e detalhes

1. Buscar pelo nome da empresa.
2. Buscar pelo CNPJ formatado.
3. Abrir a página de detalhes.

Resultado esperado: busca por nome, e-mail ou CNPJ e consulta individual funcionando.

#### 3. Edição e CNPJ imutável

1. Abrir a edição.
2. Mostrar que o CNPJ está desabilitado.
3. Alterar telefone, e-mail ou endereço.
4. Salvar.

Resultado esperado: os dados permitidos são atualizados e o CNPJ permanece igual.

#### 4. Erro e exclusão

1. Demonstrar um CNPJ inválido ou duplicado.
2. Exibir a mensagem controlada.
3. Excluir a empresa usando o diálogo de confirmação.

Resultado esperado: validação clara e exclusão com HTTP `204`.

### Dashboard

Após os cadastros ou exclusões, retornar à visão geral e atualizar a página. Explicar que os números vêm de `GET /api/dashboard/indicadores`, que executa contagens no banco sem transferir as listagens completas.

### Plano alternativo

Se a demonstração ao vivo falhar:

1. confirmar se `/health` responde;
2. mostrar o contrato no Swagger;
3. usar registros fictícios previamente cadastrados;
4. apresentar os testes automatizados como evidência;
5. evitar alterar configurações ou acessar o Neon durante a apresentação.

### Apoio visual

Usar a interface real e, ao explicar o fluxo interno, mostrar [sequencia-cadastro-aluno.mmd](sequencia-cadastro-aluno.mmd).

### Tempo sugerido

6 minutos: aproximadamente 4 minutos para alunos e 2 minutos para empresas.

## 8. Explicação do SQLAlchemy

### Objetivo da seção

Explicar como o SQLAlchemy conecta os objetos Python ao modelo relacional e como ele participa das consultas e transações.

### Sugestão de fala

> O SQLAlchemy é o ORM utilizado pelo backend. Ele permite representar as tabelas do PostgreSQL como classes Python e construir consultas tipadas sem espalhar SQL textual pela aplicação.
>
> Cada entidade declara suas colunas, chaves e relacionamentos. Quando criamos um usuário com endereço e aluno, o SQLAlchemy acompanha esse conjunto de objetos e gera os comandos de inserção na ordem exigida pelas chaves estrangeiras.
>
> O ORM não elimina as regras do banco. Unicidade, chaves estrangeiras e checks continuam sendo aplicados pelo PostgreSQL. O SQLAlchemy organiza o acesso e traduz falhas de integridade para exceções que a aplicação pode tratar.

### Mapeamento de uma entidade

Exemplo simplificado do aluno:

```python
class Aluno(Base):
    __tablename__ = "alunos"

    usuario_id: Mapped[int] = mapped_column(
        ForeignKey("usuarios.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cpf: Mapped[str] = mapped_column(
        String(11), unique=True, index=True, nullable=False
    )
    instituicao_id: Mapped[int] = mapped_column(
        ForeignKey("instituicoes_ensino.id", ondelete="RESTRICT"),
        nullable=False,
    )
    saldo: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("0.00"), nullable=False
    )
```

### Elementos utilizados

| Elemento | Função no projeto |
|---|---|
| `DeclarativeBase` | base comum de todos os models |
| `Mapped` | tipagem dos atributos persistidos |
| `mapped_column` | configuração de colunas e restrições |
| `ForeignKey` | integridade entre tabelas |
| `relationship` | navegação entre objetos relacionados |
| `back_populates` | sincronização bidirecional do relacionamento |
| `select` | construção das consultas |
| `selectinload` | carregamento eficiente dos relacionamentos |
| `Session` | unidade de trabalho com o banco |

### Relacionamentos

```python
class Usuario(Base):
    endereco = relationship(
        back_populates="usuario",
        uselist=False,
        cascade="all, delete-orphan",
    )

class Endereco(Base):
    usuario = relationship(back_populates="endereco")
```

`uselist=False` representa a relação um para um. A cascata remove o endereço órfão quando o usuário é excluído.

### Consulta real do projeto

```python
stmt = (
    select(Usuario)
    .join(Usuario.aluno)
    .options(
        selectinload(Usuario.endereco),
        selectinload(Usuario.aluno)
            .selectinload(Aluno.instituicao),
    )
    .order_by(Usuario.nome)
)
```

`selectinload` carrega os relacionamentos antecipadamente e evita executar uma nova consulta para cada aluno serializado.

### Sessão e unidade de trabalho

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Cada requisição recebe uma sessão própria. Os objetos criados ou alterados ficam associados a essa sessão até o `commit` ou `rollback`.

### Transação

```python
try:
    db.commit()
except IntegrityError:
    db.rollback()
    raise ConflictError("Dados já cadastrados")
```

No cadastro de aluno, `Usuario`, `Endereco` e `Aluno` participam da mesma transação. Uma falha impede que apenas parte do cadastro seja mantida.

### SQLAlchemy e Alembic

O SQLAlchemy define o estado atual do modelo em Python. O Alembic registra como o banco deve evoluir entre versões. Alterar uma entidade não modifica automaticamente o PostgreSQL: a mudança estrutural precisa de uma migração revisada.

### Pontos importantes para a apresentação

- ORM não significa ausência de banco relacional;
- as restrições continuam ativas no PostgreSQL;
- `Decimal` e `Numeric` preservam a precisão do saldo;
- a sessão não deve ser compartilhada entre requisições;
- `commit` e `rollback` delimitam a operação atômica;
- o frontend nunca utiliza SQLAlchemy diretamente.

### Apoio visual

Exibir [modelo-er.mmd](modelo-er.mmd) ao lado de um trecho curto de `entities.py`. Evitar mostrar o arquivo completo para manter a legibilidade.

### Tempo sugerido

2 minutos.

## 9. Demonstração do Alembic

### Objetivo da seção

Mostrar como o projeto versiona o schema do banco sem executar alterações no Neon durante a apresentação.

### Sugestão de fala

> O Alembic controla as mudanças estruturais do banco. Enquanto o SQLAlchemy descreve o estado atual das entidades em Python, cada migração registra os comandos necessários para levar o banco de uma versão para outra.
>
> Nesta Sprint 3, as alterações foram de validação, consultas, interface e documentação. Como as tabelas não mudaram, não foi necessário criar uma nova migração. A revisão inicial continua representando o schema atual.
>
> Durante esta demonstração, utilizaremos apenas comandos de inspeção ou um banco local descartável. Não aplicaremos migrações nem seeds no Neon.

### Arquivos apresentados

- `backend/alembic.ini`: configuração geral;
- `backend/alembic/env.py`: conexão, metadata e modos online/offline;
- `backend/alembic/versions/20261026_0001_sprint2.py`: revisão inicial;
- `backend/app/models/entities.py`: fonte dos metadados SQLAlchemy.

### Demonstração segura

No terminal, a partir da raiz:

```powershell
Set-Location .\backend
alembic history
```

Explicar que o histórico mostra a cadeia de revisões sem alterar o banco.

Em um ambiente local corretamente configurado, também é possível usar:

```powershell
alembic current
```

Esse comando consulta a revisão aplicada ao banco configurado. Antes de executá-lo, confirmar que `DATABASE_URL` aponta para um banco local ou descartável e que nenhuma credencial será exibida.

### Leitura da migração existente

Destacar no método `upgrade()`:

```python
def upgrade():
    op.create_table("instituicoes_ensino", ...)
    op.create_table("usuarios", ...)
    op.create_table("enderecos", ...)
    op.create_table("alunos", ...)
    op.create_table("empresas_parceiras", ...)
```

Mostrar também um exemplo de integridade:

```python
sa.ForeignKeyConstraint(
    ["instituicao_id"],
    ["instituicoes_ensino.id"],
    ondelete="RESTRICT",
)
```

### Como uma nova migração seria criada

Apresentar o comando sem executá-lo contra o Neon:

```powershell
alembic revision --autogenerate -m "descricao da alteracao"
```

Fluxo recomendado:

1. alterar os models SQLAlchemy;
2. gerar a revisão automaticamente;
3. revisar manualmente o arquivo;
4. validar em PostgreSQL descartável;
5. executar testes e verificar compatibilidade;
6. aplicar somente no ambiente autorizado.

### Aplicação local

Em um banco local ou descartável:

```powershell
alembic upgrade head
```

Esse comando modifica o banco configurado e não deve ser executado durante a apresentação se houver qualquer dúvida sobre a `DATABASE_URL` ativa.

### Downgrade

A migração possui `downgrade()`, mas a revisão inicial remove tabelas. Portanto, executar downgrade seria destrutivo e não faz parte da demonstração.

### Cuidados

- não mostrar o conteúdo do `.env`;
- não copiar a URL real do Neon para slides ou terminal;
- não executar `upgrade`, `downgrade` ou seed no Neon;
- revisar sempre o código gerado pelo `autogenerate`;
- não tratar migração como backup;
- preparar recuperação antes de alterações remotas.

### Resultado esperado

A banca deve compreender que o schema é reproduzível, versionado e consistente com as entidades SQLAlchemy, sem que a demonstração exponha credenciais ou altere dados remotos.

### Tempo sugerido

1 minuto e 30 segundos.

## 10. Testes e validações

### Objetivo da seção

Demonstrar como o projeto previne dados inválidos, protege regras cadastrais e verifica o funcionamento das integrações.

### Sugestão de fala

> O sistema aplica validações em mais de uma camada. Zod oferece feedback imediato no frontend, Pydantic protege o contrato da API e o PostgreSQL garante a integridade definitiva dos dados.
>
> Os Services complementam essas validações com regras de negócio, como instituição existente, documentos imutáveis, saldo protegido e mensagens específicas para duplicidades.
>
> Para verificar esses comportamentos, executamos testes automatizados no backend e no frontend, além do build de produção do Vite. Os testes backend usam SQLite isolado e não acessam o Neon.

### Camadas de validação

| Camada | Responsabilidade | Exemplos |
|---|---|---|
| Zod | feedback antes da chamada HTTP | formato de e-mail, CPF, CNPJ, CEP e obrigatoriedade |
| Pydantic | contrato confiável na API | tipos, limites, normalização e dígitos verificadores |
| Services | regras de negócio | duplicidades, instituição existente e campos protegidos |
| PostgreSQL | integridade definitiva | `UNIQUE`, `NOT NULL`, `CHECK`, PK e FK |

### Validação de CPF e CNPJ

O sistema não verifica apenas a quantidade de caracteres. Backend e frontend calculam os dois dígitos verificadores e rejeitam sequências repetidas.

```text
Entrada formatada
      ↓
Remove caracteres não numéricos
      ↓
Verifica quantidade e sequência repetida
      ↓
Calcula os dois dígitos verificadores
      ↓
Aceita ou rejeita o documento
```

### Campos protegidos

- `AlunoCreate` aceita CPF, mas não saldo;
- `AlunoUpdate` não possui CPF nem saldo;
- `EmpresaCreate` aceita CNPJ;
- `EmpresaUpdate` não possui CNPJ;
- campos extras não alteram os atributos protegidos;
- saldo inicial vem do model e do banco com valor zero.

### Testes backend

A suíte pytest cobre:

- cadastro válido de aluno e empresa;
- listagem e consulta de detalhes;
- edição e exclusão;
- CPF, CNPJ e e-mail duplicados;
- CPF e CNPJ com dígitos verificadores inválidos;
- instituição inexistente;
- registros inexistentes;
- buscas por diferentes campos;
- CPF, CNPJ e saldo protegidos;
- indicadores do dashboard;
- persistência após as operações.

Resultado verificado:

```text
10 passed
```

### Isolamento do banco de testes

```python
os.environ["DATABASE_URL"] = "sqlite:///./test_sprint2.db"
```

Os testes sobrescrevem a dependency `get_db`, recriam as tabelas e inserem uma instituição fictícia. Ao final, removem o banco temporário. Nenhuma chamada utiliza o Neon.

### Testes frontend

A suíte Vitest verifica:

- mensagens seguras para falhas desconhecidas da API;
- CPF válido e inválido;
- CNPJ válido e inválido;
- rejeição de sequências repetidas;
- formatação de documentos para exibição.

Resultado verificado:

```text
2 arquivos de teste aprovados
4 testes aprovados
```

### Build de produção

```powershell
Set-Location .\frontend
npm run build
```

O comando executa a verificação TypeScript e gera o bundle do Vite. O build foi concluído com sucesso.

### Demonstração no terminal

Backend:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q
```

Frontend:

```powershell
Set-Location .\frontend
npm test
npm run build
```

Mostrar somente os resultados. Não exibir variáveis de ambiente, credenciais ou dados privados.

### Limitações conhecidas

- os testes frontend ainda não executam todos os fluxos CRUD completos no navegador;
- SQLite não cobre diferenças específicas do PostgreSQL;
- autenticação e autorização não são testadas porque estão fora do escopo;
- uma validação final de migração deve usar PostgreSQL descartável antes de qualquer ambiente remoto.

### Apoio visual

Exibir a saída curta das suítes e relacionar cada grupo de testes às regras demonstradas nos CRUDs.

### Tempo sugerido

2 minutos.

## 11. Integração com PostgreSQL no Neon

### Objetivo da seção

Explicar como a API se conecta ao PostgreSQL hospedado no Neon e quais cuidados protegem as credenciais e os dados remotos.

### Sugestão de fala

> O banco utilizado pela aplicação é PostgreSQL hospedado no Neon. O frontend nunca se conecta diretamente ao banco. Somente a API FastAPI conhece a configuração de persistência.
>
> A URL de conexão é carregada do ambiente pelo Pydantic Settings. O SQLAlchemy cria o engine e utiliza o driver psycopg 3 para conversar com o PostgreSQL por uma conexão protegida com SSL.
>
> A URL real permanece no arquivo `.env`, que está ignorado pelo Git. Na apresentação mostraremos apenas o formato com placeholders e não executaremos operações de escrita, migração ou seed no banco remoto.

### Fluxo da integração

```text
React
  ↓ HTTPS / JSON
FastAPI
  ↓ SQLAlchemy
psycopg 3
  ↓ conexão TLS
PostgreSQL no Neon
```

### Configuração por ambiente

Durante a apresentação, explicar apenas que `DATABASE_URL` contém o protocolo PostgreSQL, o driver psycopg, o endereço do banco e a exigência de SSL. Não mostrar a variável completa, mesmo com dados ilustrativos, para evitar que o formato seja confundido com uma credencial real.

### Carregamento da configuração

```python
class Settings(BaseSettings):
    database_url: str = "sqlite:///./moeda_estudantil.db"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
```

Em desenvolvimento configurado para PostgreSQL, a variável do `.env` substitui o valor local padrão.

### Criação do engine

```python
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args=connect_args,
)
```

`pool_pre_ping=True` testa uma conexão antes de reutilizá-la, reduzindo erros quando uma conexão remota ficou inativa.

### Driver e SSL

- `postgresql+psycopg` seleciona PostgreSQL com psycopg 3;
- `sslmode=require` exige uma conexão criptografada;
- a senha faz parte da variável protegida e não do código;
- o frontend recebe somente `VITE_API_URL`, nunca `DATABASE_URL`.

### Demonstração recomendada

Mostrar apenas:

1. o arquivo `.env.example` com placeholders;
2. `config.py` carregando a variável;
3. `session.py` criando o engine;
4. a aplicação consultando dados fictícios pela API;
5. o diagrama [implantacao.mmd](implantacao.mmd).

Não abrir o painel do Neon nem mostrar strings de conexão durante a apresentação.

### Persistência observável pela aplicação

Uma demonstração segura pode:

1. criar um registro fictício em ambiente local;
2. recarregar a página;
3. mostrar que o registro continua disponível;
4. explicar que o mesmo mecanismo SQLAlchemy é usado com PostgreSQL quando o ambiente autorizado aponta para o Neon.

Não é necessário escrever no Neon para demonstrar a arquitetura da integração.

### Segurança

- `.env` permanece no `.gitignore`;
- `.env.example` contém somente placeholders;
- erros retornados ao cliente não incluem SQL nem URL de conexão;
- CORS aceita apenas origens configuradas;
- as credenciais devem ser diferentes entre ambientes quando possível;
- credenciais comprometidas devem ser revogadas e substituídas imediatamente.

### Limite da demonstração

Durante esta Sprint 3 não serão executados no Neon:

- `alembic upgrade` ou `downgrade`;
- seed de instituições;
- criação, atualização ou exclusão de dados;
- comandos administrativos;
- inspeção ou exposição de dados reais.

### Resultado esperado

A banca deve compreender que o Neon fornece PostgreSQL remoto, enquanto o SQLAlchemy e o psycopg fazem a integração no backend de forma configurável e sem expor o banco ao navegador.

### Tempo sugerido

1 minuto e 30 segundos.

## 12. Conclusão

### Objetivo da seção

Encerrar a apresentação retomando o que foi entregue, como a qualidade foi verificada e quais funcionalidades permanecem fora do escopo.

### Sugestão de fala

> Nesta Sprint 3, concluímos os CRUDs de alunos e empresas parceiras, incluindo cadastro, busca, detalhes, edição e exclusão. Também consolidamos as validações de CPF, CNPJ e e-mail, protegemos os documentos e o saldo e melhoramos o tratamento de erros da aplicação.
>
> A arquitetura mantém responsabilidades separadas entre React, Routers, Services, Repositories, SQLAlchemy e PostgreSQL. A persistência está documentada, possui migração Alembic e pode utilizar PostgreSQL no Neon sem expor credenciais ao frontend.
>
> Os resultados foram verificados por testes backend e frontend e pelo build de produção. Nenhuma operação foi executada no banco remoto durante esta entrega.
>
> Professores, autenticação, transações, distribuição de moedas, vantagens e resgates permanecem fora do escopo. Essas funcionalidades poderão evoluir posteriormente sobre a base cadastral e arquitetural entregue nesta sprint.

### Resultados da Sprint 3

- CRUD final de alunos;
- CRUD final de empresas parceiras;
- seleção de instituição pré-cadastrada;
- validação completa de CPF e CNPJ;
- proteção contra duplicidades;
- CPF, CNPJ e saldo protegidos;
- dashboard com indicadores consultados na API;
- arquitetura e persistência documentadas;
- diagramas Mermaid editáveis;
- testes automatizados e build aprovados.

### Evidências

```text
Backend: 10 testes aprovados
Frontend: 4 testes aprovados
Build: TypeScript e Vite concluídos
Neon: nenhuma operação remota executada
```

### Limites mantidos

Não foram implementados:

- professores;
- autenticação ou autorização;
- transações e extratos;
- distribuição de moedas;
- vantagens;
- resgates e cupons;
- notificações por e-mail.

### Encerramento sugerido

> Com isso, entregamos uma base cadastral funcional, validada e documentada, pronta para demonstração e para futuras evoluções autorizadas. Obrigado. Estamos disponíveis para perguntas.

### Slide final

Usar apenas:

```text
Conquista — Sprint 3
CRUDs finais, arquitetura e persistência

Obrigado
```

Evitar adicionar métricas, funcionalidades ou promessas que não possam ser demonstradas.

### Tempo sugerido

30 segundos.
