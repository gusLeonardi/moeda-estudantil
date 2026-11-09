%% Conquista — Componentes da Sprint 3
flowchart TB
  Browser[Navegador]

  subgraph Frontend[Frontend React]
    Routes[AppRoutes]
    Pages[Páginas de alunos, empresas e dashboard]
    Components[Componentes compartilhados]
    Clients[Services Axios]
    Routes --> Pages
    Pages --> Components
    Pages --> Clients
  end

  subgraph Backend[Backend FastAPI]
    Main[main.py]
    Routers[routers/api.py]
    Pydantic[Schemas Pydantic]
    Crud[AlunoService e EmpresaService]
    Dashboard[DashboardService]
    Repo[UsuarioRepository]
    Entities[Entidades SQLAlchemy]
    Session[SessionLocal / get_db]
    Main --> Routers
    Routers --> Pydantic
    Routers --> Crud
    Routers --> Dashboard
    Crud --> Repo
    Dashboard --> Repo
    Repo --> Entities
    Repo --> Session
  end

  Database[(PostgreSQL no Neon)]
  Migrations[Migrações Alembic]

  Browser --> Routes
  Clients -- REST / JSON --> Routers
  Session --> Database
  Entities --> Database
  Migrations -. evolui .-> Database
