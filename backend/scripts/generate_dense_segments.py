import os
import sys
import json
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.config import settings

def main():
    db_path = settings.db_path
    if not os.path.exists(db_path):
        print(f"DB not found: {db_path}")
        return

    json_path = os.path.join(os.path.dirname(db_path), "yesil_accessibility.json")
    if not os.path.exists(json_path):
        print(f"JSON not found: {json_path}")
        return

    print("Loading JSON data...")
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    nodes = data.get("nodes", {})
    edges = data.get("edges", [])

    print(f"Loaded {len(nodes)} nodes and {len(edges)} edges.")

    # We want to create about 500-1000 road segments to make the map dense but not laggy.
    # Let's group edges by name, or just take the longest ones.
    
    # Calculate edge lengths approximately
    processed_edges = []
    for edge in edges:
        n1 = str(edge["from"])
        n2 = str(edge["to"])
        if n1 not in nodes or n2 not in nodes:
            continue
        
        node1 = nodes[n1]
        node2 = nodes[n2]
        
        lat1, lon1 = node1["lat"], node1["lon"]
        lat2, lon2 = node2["lat"], node2["lon"]
        
        # Simple distance squared
        dist_sq = (lat1 - lat2)**2 + (lon1 - lon2)**2
        
        # Only take car-allowed roads for traffic?
        # Let's just take all of them, but prioritize longer ones
        processed_edges.append({
            "name": edge.get("name", "Unnamed Road"),
            "dist_sq": dist_sq,
            "poly": [[lat1, lon1], [lat2, lon2]]
        })

    # Sort by distance
    processed_edges.sort(key=lambda x: x["dist_sq"], reverse=True)
    
    # Take top 800
    top_edges = processed_edges[:800]
    
    print(f"Selected {len(top_edges)} dense segments.")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # Get locations to link to
    cur.execute("SELECT id, lat, lon FROM locations")
    locs = cur.fetchall()

    if not locs:
        print("No locations found in DB!")
        return

    # Delete existing road segments so we can replace them
    cur.execute("DELETE FROM road_segments")

    def get_closest_loc(lat, lon):
        best_id = locs[0][0]
        best_d2 = 1e18
        for lid, llat, llon in locs:
            d2 = (llat - lat)**2 + (llon - lon)**2
            if d2 < best_d2:
                best_d2 = d2
                best_id = lid
        return best_id

    print("Inserting into DB...")
    seg_id = 1
    rows = []
    for edge in top_edges:
        lat1, lon1 = edge["poly"][0]
        loc_id = get_closest_loc(lat1, lon1)
        poly_json = json.dumps(edge["poly"])
        rows.append((seg_id, edge["name"], loc_id, poly_json))
        seg_id += 1
        
        if len(rows) > 500:
            cur.executemany("INSERT INTO road_segments (id, name, location_id, polyline) VALUES (?, ?, ?, ?)", rows)
            rows = []
            
    if rows:
        cur.executemany("INSERT INTO road_segments (id, name, location_id, polyline) VALUES (?, ?, ?, ?)", rows)

    conn.commit()
    conn.close()
    
    print(f"Successfully generated {seg_id - 1} dense road segments in the database!")

if __name__ == "__main__":
    main()
