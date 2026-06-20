# backend/app/routers/admin_router.py
from fastapi import APIRouter, Depends, Header
from app.core.database import get_conn_dep
from app.models.schemas import LoginRequest
from app.services.admin_service import authenticate_admin, register_admin, get_dashboard_stats

router = APIRouter(tags=["admin"])

@router.post("/admin/login")
def api_admin_login(req: LoginRequest, conn=Depends(get_conn_dep)):
    token = authenticate_admin(conn, req.login, req.password)
    return {"token": token}

@router.post("/admin/register")
def api_admin_register(req: LoginRequest, conn=Depends(get_conn_dep)):
    token = register_admin(conn, req.login, req.password)
    return {"token": token, "message": "Тіркелу сәтті аяқталды"}

@router.get("/admin/dashboard")
def api_admin_dashboard(authorization: str = Header(None), conn=Depends(get_conn_dep)):
    return get_dashboard_stats(conn, authorization)
