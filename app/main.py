"""FastAPI application entry point."""
from fastapi import FastAPI
from app.api.chat import router as chat_router
from app.api.health import router as health_router
from app.api.upload import router as upload_router
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version='1.0.0',
    description='Document intelligence and grounded RAG API.',
)
app.include_router(health_router)
app.include_router(upload_router)
app.include_router(chat_router)


@app.get('/')
def root():
    return {'application': settings.app_name, 'status': 'running', 'docs': '/docs'}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host=settings.host, port=settings.port, reload=settings.environment == 'development')
