from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.routers.api import router
from app.services.errors import ConflictError, NotFoundError


def create_app() -> FastAPI:
    settings = get_settings()
    application = FastAPI(title=settings.app_name, version="2.0.0", docs_url="/docs")
    application.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=False, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Content-Type", "Authorization"])
    application.include_router(router, prefix=settings.api_prefix)

    @application.exception_handler(NotFoundError)
    async def not_found(_: Request, exc: NotFoundError): return JSONResponse(status_code=404, content={"detail": str(exc)})
    @application.exception_handler(ConflictError)
    async def conflict(_: Request, exc: ConflictError): return JSONResponse(status_code=409, content={"detail": str(exc)})
    @application.get("/health", tags=["infraestrutura"])
    def health(): return {"status": "ok"}
    return application


app = create_app()
