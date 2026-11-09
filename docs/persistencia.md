%% Conquista — extensão do modelo ER para o fluxo de moedas
erDiagram
  USUARIOS ||--|| ENDERECOS : possui
  USUARIOS ||--o| ALUNOS : especializa
  USUARIOS ||--o| PROFESSORES : especializa
  USUARIOS ||--o| EMPRESAS_PARCEIRAS : especializa
  INSTITUICOES_ENSINO ||--o{ ALUNOS : vincula
  INSTITUICOES_ENSINO ||--o{ PROFESSORES : vincula
  PROFESSORES ||--o{ TRANSFERENCIAS_MOEDAS : envia
  ALUNOS ||--o{ TRANSFERENCIAS_MOEDAS : recebe
  EMPRESAS_PARCEIRAS ||--o{ VANTAGENS : oferece
  ALUNOS ||--o{ RESGATES_VANTAGENS : realiza
  VANTAGENS ||--o{ RESGATES_VANTAGENS : origina
  EMPRESAS_PARCEIRAS ||--o{ RESGATES_VANTAGENS : atende

  PROFESSORES {
    int usuario_id PK,FK
    char cpf UK
    varchar departamento
    int instituicao_id FK
    numeric saldo "default 1000"
  }
  TRANSFERENCIAS_MOEDAS {
    int id PK
    int professor_id FK
    int aluno_id FK
    numeric quantidade
    varchar justificativa
    timestamp criado_em
  }
  VANTAGENS {
    int id PK
    int empresa_id FK
    varchar nome
    varchar descricao
    numeric custo
    varchar imagem_url "nullable"
    boolean ativa
    timestamp criado_em
  }
  RESGATES_VANTAGENS {
    int id PK
    int aluno_id FK
    int vantagem_id FK
    int empresa_id FK
    numeric custo
    varchar codigo_cupom UK
    varchar idempotency_key UK
    timestamp criado_em
  }
