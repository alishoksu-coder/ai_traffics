import urllib.request
import json

base_url = "http://127.0.0.1:8000"

def test_routes():
    modes = ["car_fast", "pedestrian", "barrier_free", "anti_stress"]
    start = 1
    end = 2
    
    print(f"Testing routes from {start} to {end}")
    for mode in modes:
        data = json.dumps({
            "start_node_id": start,
            "end_node_id": end,
            "mode": mode,
            "horizon_min": 30
        }).encode('utf-8')
        
        req = urllib.request.Request(f"{base_url}/routes/calculate", data=data, 
                                     headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as res:
                response_data = json.loads(res.read().decode('utf-8'))
                path_names = [n['name'] for n in response_data['path']]
                print(f"[{mode.upper()}] Time: {response_data['estimated_time_min']} min, Dist: {response_data['total_distance_m']} m")
                print(f"   Route: {' -> '.join(path_names)}")
                print("-" * 40)
        except Exception as e:
            print(f"Error {mode}: {e}")

if __name__ == "__main__":
    test_routes()
