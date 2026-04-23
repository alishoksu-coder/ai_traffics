import httpx, asyncio

async def check():
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.get("https://ai-traffics.onrender.com/vehicles")
        d = r.json()
        items = d.get("items", [])
        print(f"Vehicles count: {len(items)}")
        for v in items[:6]:
            print(f"  {v['type']:>3} #{v['id']:>2}: ({v['lat']:.4f}, {v['lon']:.4f}) -- {v['route_name']}")

asyncio.run(check())
