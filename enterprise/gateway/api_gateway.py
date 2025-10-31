"""
API Gateway - Ponto de entrada único para todos os serviços
Implementa roteamento, load balancing e rate limiting
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import httpx
from typing import Optional, Dict, Any
from core.logger import logger
from enterprise.core.service_registry import ServiceRegistry
from enterprise.core.event_bus import EventBus

app = FastAPI(
    title="JARVIS Enterprise API Gateway",
    description="Gateway unificado para microserviços JARVIS",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar componentes (serão injetados no startup)
service_registry: Optional[ServiceRegistry] = None
event_bus: Optional[EventBus] = None

@app.on_event("startup")
async def startup():
    """Inicializa componentes no startup."""
    global service_registry, event_bus
    
    service_registry = ServiceRegistry()
    event_bus = EventBus(use_redis=True)
    
    await event_bus.start()
    await service_registry.start()
    logger.info("API Gateway iniciado")

@app.on_event("shutdown")
async def shutdown():
    """Limpa recursos no shutdown."""
    global service_registry, event_bus
    
    if event_bus:
        await event_bus.stop()
    if service_registry:
        await service_registry.stop()

# Rate limiting simples (pode ser melhorado)
request_counts: Dict[str, int] = {}

def rate_limit_check(client_ip: str, limit: int = 100) -> bool:
    """Verifica rate limit."""
    count = request_counts.get(client_ip, 0)
    if count >= limit:
        return False
    request_counts[client_ip] = count + 1
    return True

@app.get("/health")
async def gateway_health():
    """Health check do gateway."""
    services_health = service_registry.get_health_summary()
    return {
        "status": "healthy",
        "gateway": "operational",
        "services": services_health
    }

@app.get("/api/{service_name:path}")
async def proxy_request(
    service_name: str,
    request: Request,
    client_ip: str = Depends(lambda r: r.client.host if r.client else "unknown")
):
    """
    Proxy genérico para serviços.
    Roteia requisições para serviços apropriados.
    """
    if not service_registry:
        raise HTTPException(status_code=503, detail="Service registry não inicializado")
    
    # Rate limiting
    if not rate_limit_check(client_ip):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Descobrir serviço
    service_url = service_registry.get_service_url(service_name)
    
    if not service_url:
        raise HTTPException(
            status_code=503,
            detail=f"Serviço {service_name} não encontrado"
        )
    
    # Proxy request
    try:
        async with httpx.AsyncClient() as client:
            # Preparar requisição
            url = f"{service_url}{request.url.path.replace('/api/', '/')}"
            params = dict(request.query_params)
            
            response = await client.request(
                method=request.method,
                url=url,
                params=params,
                headers=dict(request.headers),
                content=await request.body(),
                timeout=30.0
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Gateway timeout")
    except Exception as e:
        logger.error(f"Erro no proxy: {e}")
        raise HTTPException(status_code=502, detail=f"Bad gateway: {str(e)}")

# Rotas específicas para serviços principais
@app.post("/api/ai/generate")
async def ai_generate(request: Request):
    """Endpoint específico para geração de IA."""
    if not service_registry:
        raise HTTPException(status_code=503, detail="Service registry não inicializado")
    
    service_url = service_registry.get_service_url("ai-engine", "/generate")
    if not service_url:
        raise HTTPException(status_code=503, detail="AI Engine não disponível")
    
    data = await request.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(service_url, json=data, timeout=60.0)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

@app.post("/api/automation/execute")
async def automation_execute(request: Request):
    """Endpoint para automação."""
    if not service_registry:
        raise HTTPException(status_code=503, detail="Service registry não inicializado")
    
    service_url = service_registry.get_service_url("automation-engine", "/execute")
    if not service_url:
        raise HTTPException(status_code=503, detail="Automation Engine não disponível")
    
    data = await request.json()
    
    async with httpx.AsyncClient() as client:
        response = await client.post(service_url, json=data, timeout=30.0)
        return JSONResponse(
            content=response.json(),
            status_code=response.status_code
        )

@app.get("/api/services")
async def list_services():
    """Lista todos os serviços disponíveis."""
    if not service_registry:
        raise HTTPException(status_code=503, detail="Service registry não inicializado")
    
    services = service_registry.list_services()
    return {
        "services": [s.to_dict() for s in services]
    }

