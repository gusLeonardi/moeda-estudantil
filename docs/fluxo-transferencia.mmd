%% Conquista — transferência atômica de moedas
sequenceDiagram
  actor Admin as Operador local
  participant UI as React
  participant API as FastAPI
  participant Service as MoedasService
  participant Repo as MoedasRepository
  participant DB as PostgreSQL

  Admin->>UI: Seleciona professor, aluno, valor e justificativa
  UI->>API: POST /api/moedas/transferencias
  API->>Service: TransferenciaCreate validado
  Service->>Repo: Verifica professor e aluno
  Repo->>DB: UPDATE professor SET saldo = saldo - valor WHERE saldo >= valor
  alt saldo insuficiente
    DB-->>Repo: 0 linhas alteradas
    Service->>DB: ROLLBACK
    API-->>UI: 409 Conflict
  else débito permitido
    Repo->>DB: Credita aluno e registra transferência
    Service->>DB: COMMIT
    API-->>UI: 201 Created
  end
