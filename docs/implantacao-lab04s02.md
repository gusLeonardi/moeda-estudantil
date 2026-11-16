# Lab04S02 — Implantação do Conquista

## Estado da implantação

O Conquista está publicado em produção. O frontend e o backend foram implantados com sucesso, e a aplicação foi acessada e testada manualmente.

| Componente | Serviço | Endereço |
|---|---|---|
| Frontend React, TypeScript e Vite | Render Static Site, plano gratuito | [https://conquista-front.onrender.com](https://conquista-front.onrender.com) |
| API FastAPI | Render Web Service, plano gratuito | [https://conquista-api-dzln.onrender.com](https://conquista-api-dzln.onrender.com) |
| Verificação de saúde da API | Endpoint público | [https://conquista-api-dzln.onrender.com/health](https://conquista-api-dzln.onrender.com/health) |
| Documentação interativa da API | Swagger | [https://conquista-api-dzln.onrender.com/docs](https://conquista-api-dzln.onrender.com/docs) |
| Banco de dados | PostgreSQL no Neon | Acesso privado pelo backend |

O Render hospeda os dois serviços da aplicação. O arquivo `render.yaml` descreve o serviço Web da API. A configuração do Static Site é mantida no painel do Render. O arquivo `frontend/vercel.json` também existe no repositório, mas não representa a hospedagem atualmente publicada.

O diagrama `docs/modelagem/lab04-diagrama-implantacao.puml` foi produzido como diagrama da arquitetura planejada do Lab04 e mantém os provedores identificados como planejados. Ele não foi alterado nesta atualização; para consultar os endereços e serviços efetivos, use esta seção.

## Arquitetura implantada

```text
Navegador
  ├── HTTPS → Render Static Site (React/Vite)
  └── HTTPS/JSON + Bearer JWT → Render Web Service (FastAPI/Uvicorn)
                                  ├── PostgreSQL com TLS → Neon
                                  └── SMTP autenticado → provedor configurado (opcional)
```

O frontend é servido como arquivos estáticos pelo Render. Durante o build, `VITE_API_URL` define o endereço base da API (`https://conquista-api-dzln.onrender.com/api`). As requisições da aplicação usam HTTPS, JSON e, nas rotas protegidas, o JWT no cabeçalho `Authorization: Bearer`.

O backend obtém a URL de conexão pelo segredo `DATABASE_URL` configurado no Render. A conexão usa o driver `psycopg` e TLS exigido por `sslmode=require` (ou nível superior). O backend também pode enviar mensagens de ativação e notificações pelo serviço SMTP, quando suas variáveis estiverem configuradas.

## Resultado da publicação e validações

- **Frontend:** build de produção e publicação no Render Static Site concluídos com sucesso.
- **Backend:** publicação no Render Web Service concluída com sucesso; o serviço expõe `/health`.
- **Verificação manual:** a aplicação publicada foi acessada e testada manualmente.
- **Testes automatizados registrados no workspace:** `python -m pytest -q` — 43 aprovados; `npm test` — 19 aprovados; `npm run build` — concluído com sucesso. Esses números são os resultados documentados da validação do projeto, não uma execução feita durante esta atualização.
- **Migrações:** a cadeia foi aplicada em uma base SQLite descartável para validar a migração e a preservação de uma conta legada sem senha. Não há, neste documento, registro verificável de execução de migrações no Neon. O teste de migração em PostgreSQL isolado não foi realizado no workspace documentado: `psql` não estava instalado e o Docker não iniciou (`open //./pipe/docker_engine: The system cannot find the file specified`).
- **PlantUML:** os oito arquivos `.puml` de `docs/modelagem` foram renderizados em PNG e verificados quanto à sintaxe e apresentação; o PDF consolidado está em `output/pdf/conquista-lab04-diagramas-uml.pdf`.

Os resultados automatizados acima são registros anteriores desta validação do workspace. A confirmação de build, publicação e teste manual dos dois serviços corresponde ao estado de produção informado pela equipe.

## Render Web Service — API FastAPI

O serviço descrito em `render.yaml` usa `backend/` como diretório raiz, instala `backend/requirements.txt`, inicia o Uvicorn na porta fornecida por `$PORT` e verifica o endpoint `/health`. O comando de inicialização é:

```sh
uvicorn app.main:app --host 0.0.0.0 --port $PORT --proxy-headers
```

As migrações Alembic não são executadas automaticamente no comando de inicialização. Essa separação evita alterações de esquema não revisadas durante o reinício do serviço.

### Variáveis privadas do backend

Configure no ambiente do Render, sem adicionar os valores ao repositório:

| Variável | Finalidade |
|---|---|
| `APP_ENV` | Definir `production` para aplicar as verificações de configuração de produção. |
| `DATABASE_URL` | URL privada de conexão ao PostgreSQL Neon, com `sslmode=require` ou superior. |
| `JWT_SECRET` | Segredo aleatório forte para assinatura dos JWTs; mínimo de 32 bytes. |
| `ADMIN_CRON_TOKEN` | Segredo interno distinto de `JWT_SECRET`, também com mínimo de 32 bytes. Não é enviado ao frontend. |
| `ADMIN_UI_USERNAME` | Nome da conta administrativa institucional. |
| `ADMIN_UI_PASSWORD_HASH` | Hash Argon2 da senha administrativa; não configure a senha em texto puro. |
| `CORS_ORIGINS` | Origens HTTPS explícitas permitidas, incluindo `https://conquista-front.onrender.com`; não use `*`. |
| `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` | Dados do provedor de e-mail. São opcionais para iniciar a API; os fluxos de e-mail dependem da configuração. |

Para gerar o hash Argon2 da senha administrativa localmente, no PowerShell:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe .\scripts\hash_admin_password.py
```

Configure a saída somente como valor privado do backend no Render. Nunca publique segredos nos logs, no frontend, no histórico do terminal ou no Git.

O endpoint interno `POST /api/professores` e o endpoint de crédito semestral exigem `X-Admin-Token`, comparado com `ADMIN_CRON_TOKEN`. O gerenciamento de professores pela interface administrativa usa uma conta administrativa separada, autenticada por JWT. Não use o token de cron no navegador.

## Render Static Site — frontend React/Vite

O serviço está publicado em `https://conquista-front.onrender.com`. Configure o diretório publicado como `frontend/`, o comando de instalação como `npm ci`, o comando de build como `npm run build` e a saída como `dist`.

Configure a seguinte variável no ambiente de build do Static Site:

```dotenv
VITE_API_URL=https://conquista-api-dzln.onrender.com/api
```

`VITE_API_URL` é incorporada aos arquivos JavaScript gerados e, portanto, é pública. Ela deve conter apenas o endereço base da API, nunca senhas, tokens ou outras credenciais. As regras de navegação SPA e os cabeçalhos presentes em `frontend/vercel.json` são configuração do Vercel e não substituem a configuração efetiva do serviço Render.

## CORS e comunicação entre serviços

O backend usa `CORS_ORIGINS` como uma lista separada por vírgulas. Em produção, configure somente origens HTTPS necessárias, incluindo a origem do Static Site:

```dotenv
CORS_ORIGINS=https://conquista-front.onrender.com
```

Não inclua curingas. O frontend envia o JWT por `Authorization`; a API permite esse cabeçalho e os métodos HTTP utilizados pelo sistema. Para domínios de prévia, adicione somente origens específicas e necessárias.

## Neon — PostgreSQL

O banco de produção é PostgreSQL no Neon. A URL deve permanecer como variável secreta do serviço backend no Render, usar o driver `postgresql+psycopg` e exigir TLS, por exemplo:

```text
postgresql+psycopg://<usuario>:<senha>@<host>/<banco>?sslmode=require
```

Os valores entre sinais `< >` são marcadores de exemplo e devem ser substituídos somente no painel privado do provedor. Antes de executar uma migration, confirme o banco e o branch Neon selecionados, revise a migration e tenha um plano de recuperação. Não execute comandos de migration contra produção apenas para validar o ambiente local.

As migrations `20261116_0006` e `20261116_0007` adicionam, respectivamente, armazenamento de ativações temporárias e contadores de limitação de tentativas. A cadeia de migrations foi validada em SQLite descartável. Este documento não afirma que uma migração específica foi executada no Neon, pois não há registro verificável dessa execução.

## SMTP e envio de e-mails

O backend usa configuração SMTP por ambiente para enviar convites de ativação e notificações de operações. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` e `SMTP_FROM` no Render quando o envio estiver habilitado. Não registre valores secretos no repositório. Sem uma entrega SMTP bem-sucedida, tokens de ativação não são mantidos como convites utilizáveis e o fluxo administrativo permite nova tentativa de envio.

## Sessões e proteção

O frontend mantém o JWT em `sessionStorage`, remove a sessão no logout e limpa o token diante de resposta 401. O armazenamento temporário reduz a persistência entre sessões do navegador, mas não impede que código JavaScript da mesma origem acesse o token durante uma sessão. Uma vulnerabilidade XSS pode expô-lo. Use HTTPS, mantenha dependências atualizadas e não renderize HTML não confiável. Uma alternativa futura é uma sessão em cookie `HttpOnly; Secure; SameSite`, que exigiria mudanças coordenadas na autenticação e no CORS.

Login e solicitação de ativação usam contadores persistidos no PostgreSQL, por IP e e-mail normalizados; as chaves são protegidas por HMAC. Os limites configurados são 5 tentativas por e-mail e 20 por IP a cada 15 minutos no login, e 3 por e-mail e 10 por IP por hora na solicitação de ativação. Ao exceder o limite, a API responde com HTTP 429 e `Retry-After`. Em produção, o código prioriza o cabeçalho `CF-Connecting-IP`; não confia em `X-Forwarded-For` enviado pelo cliente para identificar a origem.

## Execução e validação local

Para executar os testes sem acessar os dados de produção:

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest -q

Set-Location ..\frontend
npm ci
npm test
npm run build
```

Para iniciar a API localmente, aplique as migrations somente a um banco local ou isolado e execute Uvicorn a partir de `backend/`:

```powershell
Set-Location .\backend
..\.venv\Scripts\alembic.exe upgrade head
..\.venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000
```

Para verificar a aplicação publicada, acesse o frontend, confira uma rota interna após recarregar a página e consulte `/health` no endereço da API. A publicação e os testes manuais descritos na seção de estado correspondem à confirmação da equipe; esta atualização documental não repetiu o teste externo.

## Diagramas do Lab04

Os fontes PlantUML editáveis e os PNGs ficam em `docs/modelagem/`:

- `lab04-seq-autenticacao` — login e ativação de conta antiga;
- `lab04-seq-transferencia` — transferência de moedas;
- `lab04-seq-resgate` — resgate idempotente de vantagem;
- `lab04-seq-cupom` — consulta e validação de cupom pela empresa proprietária;
- `lab04-seq-admin-professores` — gerenciamento administrativo de professores;
- `lab04-sequencias` — fluxos principais alternativos por perfil;
- `lab04-visao-geral-interacao` — Diagrama de Visão Geral de Interação UML com decisões e referências às sequências;
- `lab04-diagrama-implantacao` — arquitetura de implantação planejada, conforme explicado acima.

O documento consolidado está em `output/pdf/conquista-lab04-diagramas-uml.pdf`.

## Referências de plataforma

- [Render — especificação de Blueprints](https://render.com/docs/blueprint-spec);
- [Render — verificações de integridade](https://render.com/docs/health-checks);
- [Render — sites estáticos](https://render.com/docs/static-sites);
- [Cloudflare — cabeçalhos de endereço IP](https://developers.cloudflare.com/fundamentals/reference/http-headers/).
