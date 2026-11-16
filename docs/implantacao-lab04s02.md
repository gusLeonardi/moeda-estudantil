# Lab04S02 — Preparação de implantação

## Estado

Os arquivos de configuração para Render e Vercel estão preparados. O serviço ainda não foi publicado e nenhuma URL pública foi verificada. O Neon não foi migrado. O diagrama em `docs/modelagem/lab04-diagrama-implantacao.puml` marca os provedores como planejados.

## Validacao deste workspace

- Backend: `python -m pytest -q` — 37 passed.
- Frontend: `npm test` — 9 passed; `npm run build` — sucesso.
- Alembic: a cadeia completa foi aplicada no teste SQLite descartavel, que confirmou a preservacao do usuario legado sem senha.
- PostgreSQL isolado: nao executado; `psql` nao esta instalado e o daemon Docker nao respondeu (`open //./pipe/docker_engine: The system cannot find the file specified`).
- PlantUML 1.2026.10: renderizados os quatro diagramas de sequencia, a visao geral de interacao e o diagrama de implantacao. As imagens PNG ficam ao lado das fontes editaveis.

## Render — API FastAPI

O Blueprint `render.yaml` aponta o serviço para `backend/`, instala `requirements.txt`, inicia Uvicorn na porta `$PORT`, desativa deploy automático e verifica `/health`. As migrations ficam fora do comando de inicialização para evitar alterações silenciosas no banco compartilhado.

Configure no Render, em variáveis privadas:

- `APP_ENV=production`
- `DATABASE_URL`: URL do Neon no formato `postgresql+psycopg://.../neondb?sslmode=require`
- `JWT_SECRET`: segredo aleatório forte (pelo menos 32 bytes)
- `ADMIN_CRON_TOKEN`: segredo distinto de `JWT_SECRET`
- `CORS_ORIGINS`: origem exata do frontend publicado, sem `*`
- `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`: provedor de e-mail; sem SMTP, ativações não são entregues e seus grants são invalidados

O endpoint de professor sempre exige `X-Admin-Token`, mesmo em `APP_ENV=development`. Execute-o apenas por uma operação administrativa autenticada fora do navegador. Não coloque essa credencial no React/Vercel.

### Migration manual e controlada

Revise o SQL antes de apontar o comando para uma base compartilhada. A migration `20261116_0007` cria apenas a tabela de contadores de autenticação; a cadeia anterior cria a tabela de ativações. Não há drops ou alterações de dados existentes.

```powershell
Set-Location .\backend
$env:DATABASE_URL = "postgresql+psycopg://<usuario>:<senha>@<host>/<database>?sslmode=require"
..\.venv\Scripts\alembic.exe upgrade head
```

Execute primeiro contra um banco PostgreSQL isolado e somente depois de aprovação explícita para o banco compartilhado. Nunca copie a URL real para o repositório, terminal compartilhado ou logs.

## Vercel — frontend React

Configure a raiz do projeto como `frontend/`. O `frontend/vercel.json` define `npm ci`, `npm run build`, saída `dist`, fallback SPA para `index.html` e cabeçalhos básicos. Configure `VITE_API_URL=https://<url-do-render>/api` no painel da Vercel para Preview e Production; a variável é incorporada ao bundle e não pode conter segredo.

Após publicar o frontend, configure no Render `CORS_ORIGINS` com a URL de produção e, se necessário, uma URL de preview específica. Evite curingas.

## Neon — PostgreSQL

Use a URL de conexão com TLS (`sslmode=require`) como `DATABASE_URL` secreto do Render. Confirme o branch/database escolhido antes de qualquer migration e mantenha backups/ponto de restauração conforme a política da conta. Nenhuma migration foi executada nesta entrega.

## Sessões e proteção

O frontend guarda o JWT em `sessionStorage`, remove o valor antigo do `localStorage` e limpa a sessão no logout/401. Isso reduz a persistência entre sessões do navegador, mas o token continua acessível a JavaScript da origem: uma vulnerabilidade XSS pode roubá-lo enquanto a sessão estiver ativa. Portanto, mantenha dependências atualizadas, não renderize HTML não confiável, use HTTPS e aplique uma política CSP adequada ao domínio publicado. Uma evolução mais forte é mover a sessão para cookie `HttpOnly; Secure; SameSite` com proteção CSRF, o que exige alteração coordenada de CORS e autenticação.

## Limites de tentativas

Login e solicitação de ativação usam contadores PostgreSQL atômicos, limitados por endereço e por e-mail normalizados; as chaves persistidas são HMAC e não guardam e-mails/IPs em claro. Em produção Render, o código usa `CF-Connecting-IP`; o cabeçalho `X-Forwarded-For` não é confiável para identificar clientes. Os limites são 5 logins por e-mail e 20 por IP a cada 15 minutos; para ativação, 3 por e-mail e 10 por IP por hora. Ao atingir o limite, a API responde `429` com `Retry-After`.

## Verificações locais

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q
..\.venv\Scripts\alembic.exe upgrade head
..\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000

Set-Location ..\frontend
npm test
npm run build
```

Para validar migration PostgreSQL, use apenas uma instância/container temporário isolado, nunca a URL Neon compartilhada. Para verificar publicação, teste `/health` do Render e carregue o domínio Vercel, incluindo uma rota SPA recarregada diretamente.

## Referências de plataforma

- [Render Blueprint specification](https://render.com/docs/blueprint-spec)
- [Render health checks](https://render.com/docs/health-checks)
- [Vercel `vercel.json`](https://vercel.com/docs/project-configuration/vercel-json)
- [Cloudflare visitor IP headers](https://developers.cloudflare.com/fundamentals/reference/http-headers/)
