import os
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_path = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(backend_path))

import uvicorn

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"==================================================================")
    print(f" Cognitive Assistance & Interview Preparation Bot")
    print(f" URL: http://127.0.0.1:{port}")
    print(f" Swagger Docs: http://127.0.0.1:{port}/docs")
    print(f"==================================================================")
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=True, app_dir=str(backend_path))
