from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "API de Monitoramento de Descarte Ilegal funcionando"}

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": str(datetime.now())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple:app", host="0.0.0.0", port=8000, reload=True) 