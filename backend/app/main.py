from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.routers import generator

import os

app = FastAPI(
    title="YeHub Entropy Generator",
    description="API para geração de senhas e passphrases com alta entropia.",
    version="1.0.0"
)

# --- Configuração de CORS (Crucial para o Frontend funcionar) ---
# Em produção, você substituiria "*" pelos domínios reais (ex: ["https://yehub.com"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Permite que qualquer site (incluindo seu arquivo HTML local) chame a API
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, etc.
    allow_headers=["*"],
)

# --- Servindo o Frontend Estático ---
# Montamos a pasta frontend para ser acessível via /static
frontend_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Rota para entregar o index.html principal na raiz (/)
@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

# --- Incluindo as Rotas da API ---
app.include_router(generator.router)

@app.get("/health", tags=["System"])
async def health_check():
    """Rota para verificar se a API está online."""
    return {"status": "online", "message": "YeHub API is running"}