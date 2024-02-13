"""
Main process. This file is the entry point to start the backend.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from countdart.api import router


def create_app() -> FastAPI:
    """Create the FastAPI app and include the router."""

    app = FastAPI(
        title="Count Dart",
    )
    origins = ["*"]

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
