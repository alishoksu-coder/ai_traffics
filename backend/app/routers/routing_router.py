# backend/app/routers/routing_router.py
from fastapi import APIRouter
from app.models.schemas import RouteCalculateRequest
from app.services.routing_service import calculate_multicriteria_route, get_routing_nodes

router = APIRouter(tags=["routing"])

@router.post("/routes/calculate")
def api_calculate_route(req: RouteCalculateRequest):
    return calculate_multicriteria_route(req.start_node_id, req.end_node_id, req.mode, req.horizon_min)

@router.get("/routes/nodes")
def api_get_nodes():
    return get_routing_nodes()
