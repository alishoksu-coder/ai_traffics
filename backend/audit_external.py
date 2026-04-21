"""
POLNAYA PROVERKA GOTOVNOSTI K VNESHEMU TESTIROVANIYU
AI Traffic - External Readiness Audit
"""
import httpx
import asyncio
import time
import sys
import io

# Fix Windows encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://ai-traffics.onrender.com"

PASSED = 0
FAILED = 0
WARNINGS = 0

def ok(msg):
    global PASSED
    PASSED += 1
    print(f"  [OK] {msg}")

def fail(msg):
    global FAILED
    FAILED += 1
    print(f"  [FAIL] {msg}")

def warn(msg):
    global WARNINGS
    WARNINGS += 1
    print(f"  [WARN] {msg}")

async def run_full_audit():
    global PASSED, FAILED, WARNINGS

    async with httpx.AsyncClient(timeout=30.0) as c:

        print("\n=== 1. DOSTUPNOST SERVERA ===")
        try:
            t0 = time.time()
            r = await c.get(f"{BASE_URL}/health")
            latency = time.time() - t0
            if r.status_code == 200 and r.json().get("status") == "ok":
                ok(f"Health check proyden ({latency:.2f}s)")
            else:
                fail(f"Health check vernul {r.status_code}")
        except Exception as e:
            fail(f"Server nedostupen: {e}")

        print("\n=== 2. CORS ZAGOLOVKI ===")
        try:
            r = await c.options(f"{BASE_URL}/locations", headers={
                "Origin": "https://alishoksu-coder.github.io",
                "Access-Control-Request-Method": "GET"
            })
            acao = r.headers.get("access-control-allow-origin", "")
            if acao == "*" or "github.io" in acao:
                ok(f"CORS razreshaet vneshnie zaprosy (Allow-Origin: {acao})")
            else:
                warn(f"CORS mozhet blokirovat zaprosy (Allow-Origin: '{acao}')")
        except Exception as e:
            warn(f"Ne udalos proverit CORS: {e}")

        print("\n=== 3. OSNOVNYE API ENDPOINTS ===")

        # 3.1 Locations
        try:
            r = await c.get(f"{BASE_URL}/locations")
            data = r.json()
            items = data.get("items", [])
            if r.status_code == 200 and len(items) > 0:
                ok(f"/locations — {len(items)} lokaciy zagruzheno")
            else:
                fail(f"/locations — pustoy spisok ili oshibka")
        except Exception as e:
            fail(f"/locations — {e}")

        # 3.2 Traffic Map
        for horizon in [0, 30, 60]:
            try:
                r = await c.get(f"{BASE_URL}/traffic/map?horizon={horizon}")
                data = r.json()
                items = data.get("items", [])
                if r.status_code == 200 and len(items) > 0:
                    ok(f"/traffic/map?horizon={horizon} — {len(items)} tochek")
                else:
                    fail(f"/traffic/map?horizon={horizon} — pustoy otvet")
            except Exception as e:
                fail(f"/traffic/map?horizon={horizon} — {e}")

        # 3.3 Road Segments (karta)
        try:
            r = await c.get(f"{BASE_URL}/roads/segments?horizon=0")
            data = r.json()
            items = data.get("items", [])
            if r.status_code == 200 and len(items) > 0:
                ok(f"/roads/segments — {len(items)} segmentov (veb-karta budet rabotat)")
            else:
                fail(f"/roads/segments — pustoy otvet (veb-karta budet pustoy!)")
        except Exception as e:
            fail(f"/roads/segments — {e}")

        # 3.4 Weather
        try:
            r = await c.get(f"{BASE_URL}/weather")
            data = r.json()
            if r.status_code == 200 and "temp" in data:
                ok(f"/weather — {data['temp']}C, {data.get('description','')}")
            else:
                fail(f"/weather — nekorrektnyy otvet")
        except Exception as e:
            fail(f"/weather — {e}")

        # 3.5 Recommendation
        try:
            r = await c.get(f"{BASE_URL}/traffic/recommendation")
            data = r.json()
            if r.status_code == 200 and "message" in data:
                ok(f"/traffic/recommendation — AI sovet poluchen")
            else:
                fail(f"/traffic/recommendation — net message")
        except Exception as e:
            fail(f"/traffic/recommendation — {e}")

        # 3.6 AR Points
        try:
            r = await c.get(f"{BASE_URL}/traffic/ar_points?horizon=30")
            data = r.json()
            ar = data.get("ar_points", [])
            ok(f"/traffic/ar_points — {len(ar)} problemnyh zon")
        except Exception as e:
            fail(f"/traffic/ar_points — {e}")

        # 3.7 Accuracy
        try:
            r = await c.get(f"{BASE_URL}/traffic/accuracy?horizon=30")
            data = r.json()
            if r.status_code == 200 and "mae" in data:
                ok(f"/traffic/accuracy — MAE={data['mae']:.2f}, RMSE={data['rmse']:.2f}")
            else:
                warn(f"/traffic/accuracy — nestandartnyy otvet: {r.status_code}")
        except Exception as e:
            fail(f"/traffic/accuracy — {e}")

        # 3.8 Parking
        try:
            r = await c.get(f"{BASE_URL}/parking")
            data = r.json()
            items = data.get("items", [])
            if r.status_code == 200:
                ok(f"/parking — {len(items)} parkovok")
            else:
                warn(f"/parking — {r.status_code}")
        except Exception as e:
            warn(f"/parking — {e}")

        print("\n=== 4. MARSHRUTIZACIYA (4 rezhima) ===")
        try:
            r = await c.get(f"{BASE_URL}/routes/nodes")
            nodes = r.json()["nodes"]
            if len(nodes) >= 2:
                ok(f"/routes/nodes — {len(nodes)} uzlov dostupno")
                start = nodes[0]["node_id"]
                end = nodes[-1]["node_id"]

                modes = ["car_fast", "pedestrian", "barrier_free", "anti_stress"]
                for mode in modes:
                    try:
                        rr = await c.post(f"{BASE_URL}/routes/calculate", json={
                            "start_node_id": start,
                            "end_node_id": end,
                            "mode": mode
                        })
                        if rr.status_code == 200:
                            d = rr.json()
                            ok(f"  {mode}: {d['total_distance_m']:.0f}m, {d['estimated_time_min']:.1f} min")
                        else:
                            fail(f"  {mode}: kod {rr.status_code}")
                    except Exception as e:
                        fail(f"  {mode}: {e}")
            else:
                fail(f"/routes/nodes — menee 2 uzlov")
        except Exception as e:
            fail(f"/routes/nodes — {e}")

        print("\n=== 5. DIGITAL TWIN (simulyaciya probki) ===")
        try:
            r = await c.post(f"{BASE_URL}/traffic/simulate_closure", json={
                "lat": 51.1283, "lon": 71.4305, "duration_min": 5
            })
            if r.status_code == 200 and r.json().get("status") == "success":
                ok("simulate_closure — incident sozdan uspeshno")
            else:
                fail(f"simulate_closure — {r.status_code}")
        except Exception as e:
            fail(f"simulate_closure — {e}")

        print("\n=== 6. ADMIN PANEL ===")
        try:
            r = await c.get(f"{BASE_URL}/admin/dashboard")
            if r.status_code == 401:
                ok("Adminka zashchishchena avtorizaciey (401 bez tokena)")
            elif r.status_code == 200:
                warn("Adminka dostupna bez tokena (proveryte bezopasnost)")
            else:
                warn(f"Adminka vernula {r.status_code}")
        except Exception as e:
            fail(f"Adminka — {e}")

    print("\n" + "=" * 50)
    print(f"  ITOGO: [OK] {PASSED} | [FAIL] {FAILED} | [WARN] {WARNINGS}")
    print("=" * 50)

    if FAILED == 0:
        print("\n  PROEKT POLNOSTYU GOTOV K VNESHNEMU TESTIROVANIYU!")
    elif FAILED <= 2:
        print("\n  Proekt pochti gotov. Ispravte oshibki vyshe.")
    else:
        print("\n  Est kriticheskie problemy. Vneshniy test poka nevozmozhen.")

if __name__ == "__main__":
    asyncio.run(run_full_audit())
