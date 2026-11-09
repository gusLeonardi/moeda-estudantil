%% Conquista — resgate idempotente de vantagem
sequenceDiagram
  actor Admin as Operador local
  participant UI as React
  participant API as FastAPI
  participant Service as ResgateService
  participant Repo as VantagemRepository
  participant DB as PostgreSQL

  Admin->>UI: Seleciona aluno e vantagem
  UI->>API: POST /api/resgates com idempotency_key
  API->>Service: ResgateCreate validado
  Service->>Repo: Procura pedido pela chave
  alt pedido já processado
    Repo-->>Service: Resgate existente
    API-->>UI: Mesmo cupom, sem novo débito
  else novo pedido
    Service->>Repo: Verifica vantagem ativa
    Repo->>DB: UPDATE aluno SET saldo = saldo - custo WHERE saldo >= custo
    alt saldo insuficiente
      DB-->>Repo: 0 linhas alteradas
      Service->>DB: ROLLBACK
      API-->>UI: 409 Conflict
    else débito permitido
      Repo->>DB: Registra resgate e cupom único
      Service->>DB: COMMIT
      API-->>UI: 201 Created com cupom
    end
  end
