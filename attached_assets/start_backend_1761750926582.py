#!/usr/bin/env python3
import os
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.app.main:app",
        host="localhost",
        port=int(os.getenv("BACKEND_PORT", "8000")),
        reload=True,
        log_level="info"
    )
