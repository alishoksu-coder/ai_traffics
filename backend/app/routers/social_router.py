# backend/app/routers/social_router.py
from fastapi import APIRouter, Depends
import time

from app.core.database import get_conn_dep
from app.models.schemas import AddFriendRequest, MeetingRequest, SmartMeetRequest, UserEventRequest
from app.repositories.user_repository import get_friends, add_friend, get_user_meetings, create_meeting, commit
from app.services.friends_service import calculate_smart_meet
from app.services.simulation_service import sim

router = APIRouter(tags=["social"])

@router.get("/friends")
def api_friends_list(conn=Depends(get_conn_dep)):
    return {"items": get_friends(conn)}

@router.post("/friends")
def api_friends_add(req: AddFriendRequest, conn=Depends(get_conn_dep)):
    fid = add_friend(conn, req.name)
    commit(conn)
    return {"id": fid, "name": req.name}

@router.get("/meetings")
def api_meetings_list(user_id: str, conn=Depends(get_conn_dep)):
    return {"items": get_user_meetings(conn, user_id)}

@router.post("/meetings")
def api_meetings_create(req: MeetingRequest, conn=Depends(get_conn_dep)):
    mid = create_meeting(conn, req.user_id, req.friend_id, req.location_id, req.meeting_time)
    commit(conn)
    return {"id": mid, "status": "success"}

@router.post("/smart_meet")
def api_smart_meet(req: SmartMeetRequest, conn=Depends(get_conn_dep)):
    return calculate_smart_meet(conn, req.user_locations, req.meeting_time_offset_min)

@router.post("/events")
def api_create_event(req: UserEventRequest, conn=Depends(get_conn_dep)):
    cur = conn.cursor()
    now = int(time.time())
    cur.execute(
        "INSERT INTO user_events (event_type, lat, lng, created_at) VALUES (?, ?, ?, ?)",
        (req.event_type, req.lat, req.lng, now)
    )
    commit(conn)
    
    strength = 80.0 if req.event_type == "accident" else (60.0 if req.event_type == "repair" else 20.0)
    sim.add_custom_hotspot(req.lat, req.lng, strength=strength, radius_deg=0.01, ttl_seconds=3600)
    
    return {"status": "success", "id": cur.lastrowid}

@router.get("/events")
def api_get_events(conn=Depends(get_conn_dep)):
    now = int(time.time())
    threshold = now - 7200
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, event_type, lat, lng, created_at FROM user_events WHERE created_at > ?",
        (threshold,)
    ).fetchall()
    
    items = []
    for r in rows:
        items.append({
            "id": r[0],
            "event_type": r[1],
            "lat": r[2],
            "lng": r[3],
            "created_at": r[4]
        })
    return {"items": items}
