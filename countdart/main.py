"""Main process. This file is the entry point to start the backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from countdart.api import router
from countdart.database import get_session, init_db

# TODO: Replace with settings
API_V1_STR = "/api/v1"


def create_app() -> FastAPI:
    """Create the FastAPI app and include the router."""

    app = FastAPI(
        title="Count Dart",
        openapi_url=f"{API_V1_STR}/openapi.json",
        docs_url=f"{API_V1_STR}/docs",
        redoc_url=f"{API_V1_STR}/redoc",
    )
    origins = ["*"]

    init_db(get_session())

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():
        return {"status": "ok"}

    app.include_router(router)

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "countdart.main:create_app",
        host="127.0.0.1",
        port=7860,
        log_level="debug",
        reload=True,
    )
