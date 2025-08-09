from fastapi import FastAPI

from .api import router as api_router


def create_app() -> FastAPI:
    app = FastAPI(title="Event Audit API")
    app.include_router(api_router, prefix="/api/v1")
    return app


app = create_app()


