from __future__ import annotations

from fastapi import FastAPI

from fdc.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(title="financial_data_center_lt API", version="0.1.0")
    app.include_router(router)
    return app
