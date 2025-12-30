import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime # Importante para o teste imediato

from app.core.database import db
from app.routes import auth, ml_auth, lojas, products
from app.services.token_manager import refresh_expiring_tokens
from fastapi.middleware.cors import CORSMiddleware  # <--- FALTAVA ESSA LINHA

# Cria o agendador
scheduler = AsyncIOScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- INICIO ---
    print("🚀 Iniciando Scheduler de Tokens...")
    
    # TESTE: Roda AGORA e repete a cada 10 segundos
    scheduler.add_job(refresh_expiring_tokens, 'interval', minutes=15, next_run_time=datetime.now())
    
    scheduler.start()
    
    yield # O App roda aqui
    
    # --- FIM ---
    print("🛑 Parando Scheduler...")
    scheduler.shutdown()

# Passa o lifespan para o FastAPI
app = FastAPI(lifespan=lifespan)

# Rotas
app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
app.include_router(ml_auth.router, prefix="/ml", tags=["Mercado Livre"])
app.include_router(lojas.router, prefix="/api", tags=["Lojas"])
app.include_router(products.router, prefix="/products", tags=["Produtos"]) # <--- Adicionar

# ... imports

# Configurar CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",    # <--- ADICIONE ESTA LINHA (Vite Localhost)
    "http://127.0.0.1:5173",    # <--- ADICIONE ESTA LINHA (Vite IP)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Ou use ["*"] para liberar TUDO (modo preguiçoso/dev)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "API Hub ML rodando!"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
