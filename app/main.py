from fastapi import FastAPI

from app.api.auth import router as auth_router
from app.api.prompts import router as prompts_router
from app.api.collections import router as collctions_router
from app.api.optimizer import router as optimize_router
from app.api.scorer import router as scorer_router

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(
    title="PromptStudio API",
    version="1.0.0"
)

app.include_router(auth_router)
app.include_router(prompts_router)
app.include_router(collctions_router)
app.include_router(optimize_router)
app.include_router(scorer_router)



@app.get("/")
def root():
    return {
        "message": "PromptStudio API"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
origins = [
    "http://localhost:5173",
    "https://promptstudio-tawny.vercel.app",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
