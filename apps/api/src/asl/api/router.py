from fastapi import APIRouter

from asl.api.v1 import approvals, govern, health

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(govern.router, tags=["govern"])
api_router.include_router(approvals.router, tags=["approvals"])
