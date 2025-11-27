from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.routers import candidates, vectors

app = FastAPI()


@app.get("/")
def read_root():
    return RedirectResponse("/docs")


@app.get("/healthcheck")
async def health_check():
    return {"status": "ok"}


app.include_router(candidates.router, tags=["Candidates"], prefix="/candidates")
app.include_router(vectors.router, tags=["Vectors"], prefix="/vectors")
