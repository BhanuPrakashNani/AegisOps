from fastapi import FastAPI

app = FastAPI(
    title="AegisOps",
    description="Autonomous LLMOps Platform",
    version="0.1.0"
)

@app.get("/")
def root():
    return {
        "service": "AegisOps",
        "status": "running" 
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }