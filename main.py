"""
Railway deployment wrapper for ResuMatch backend.
Always defines a valid ASGI `app`, then tries to load backend/main.py and replace it.
"""

import os
import sys
import json
import importlib.util
from types import ModuleType
from typing import Any, Dict

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")
BACKEND_MAIN_PATH = os.path.join(BACKEND_DIR, "main.py")

# Minimal ASGI fallback that requires no third-party imports
async def app(scope: Dict[str, Any], receive, send):  # type: ignore[override]
    if scope.get("type") != "http":
        # Only HTTP supported in fallback
        await send({"type": "http.response.start", "status": 404, "headers": []})
        await send({"type": "http.response.body", "body": b""})
        return
    path = scope.get("path", "/")
    if path == "/healthz":
        body = json.dumps({"status": "error", "message": "backend not loaded"}).encode()
        headers = [(b"content-type", b"application/json")]
        await send({"type": "http.response.start", "status": 503, "headers": headers})
        await send({"type": "http.response.body", "body": body})
    else:
        await send({"type": "http.response.start", "status": 404, "headers": []})
        await send({"type": "http.response.body", "body": b""})

# Allow absolute imports inside backend (e.g., `from routes import ...`)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

def _load_backend(module_path: str, module_name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {module_name} at {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)  # type: ignore[attr-defined]
    return module

# Try to swap in the real app from backend
try:
    backend_main = _load_backend(BACKEND_MAIN_PATH, "resumatch_backend_main")
    loaded_app = getattr(backend_main, "app", None)
    if loaded_app is None:
        # Try 'api' if 'app' doesn't exist
        loaded_app = getattr(backend_main, "api", None)
    if loaded_app is None:
        print("⚠️ WARNING: Neither 'app' nor 'api' found in backend/main.py")
    else:
        app = loaded_app
        # Also expose under 'api' name for compatibility with Procfile configs
        api = app  # type: ignore[assignment]
        print(f"✅ Loaded backend app: {type(app)}")
except Exception as e:
    print(f"❌ Failed to load backend: {e}")
    # Keep fallback app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)


