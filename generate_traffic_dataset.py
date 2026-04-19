import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_traffic_dataset(num_records=50000):
    print(f"Generating {num_records} records of traffic history for Yesil district...")
    
    # Intersections in Yesil district
    intersections = [
        "Mangilik_El_Syganak",
        "Turan_Syganak",
        "Kabanbay_Kunaev",
        "Dostyk_Turkistan",
        "Mangilik_El_Kunaev"
    ]
    
    weather_conditions = ["Clear", "Rain", "Snow", "Fog"]
    weather_probs = [0.65, 0.15, 0.15, 0.05]
    
    # Start date for history
    start_date = datetime(2025, 1, 1, 0, 0)
    
    data = []
    
    # Generate data
    current_time = start_date
    for i in range(num_records):
        intersection = random.choice(intersections)
        
        # Determine time-based patterns
        hour = current_time.hour
        month = current_time.month
        day_of_week = current_time.weekday()
        
        is_weekend = 1 if day_of_week >= 5 else 0
        is_peak_hour = 1 if (7 <= hour <= 9) or (17 <= hour <= 20) else 0
        
        # Base traffic volume depends on time
        base_volume = random.randint(500, 1500)
        if is_peak_hour and not is_weekend:
            base_volume += random.randint(1500, 3000)
        elif is_weekend:
            base_volume -= random.randint(200, 400)
        
        # Night time is very quiet
        if 0 <= hour <= 5:
            base_volume = random.randint(50, 300)
            
        vehicle_count = max(0, base_volume)
        
        # Weather and season effects
        weather = np.random.choice(weather_conditions, p=weather_probs)
        
        # Speed inversely correlated with volume
        base_speed = 60 # km/h limit usually
        if vehicle_count > 3000:
            avg_speed = random.randint(5, 20)
        elif vehicle_count > 1500:
            avg_speed = random.randint(20, 40)
        else:
            avg_speed = random.randint(40, 65)
            
        # Bad weather reduces speed
        if weather in ["Snow", "Fog"]:
            avg_speed = int(avg_speed * 0.7)
        elif weather == "Rain":
            avg_speed = int(avg_speed * 0.85)
            
        # Astana approximate temperature by month
        if month in [12, 1, 2]:
            temp = random.randint(-30, -5)
        elif month in [3, 4, 10, 11]:
            temp = random.randint(-10, 15)
        else:
            temp = random.randint(15, 35)
            
        # Accidents are rare, more likely in bad weather or high traffic
        accident_prob = 0.001
        if weather in ["Snow", "Fog"] or is_peak_hour:
            accident_prob = 0.005
        accident = 1 if random.random() < accident_prob else 0
        
        # If accident, speed drops drastically
        if accident:
            avg_speed = random.randint(0, 10)
            
        # Target variable for LSTM: Congestion Level (0.0 to 1.0)
        # 1.0 means severe jam: low speed, high volume
        congestion = 1.0 - (avg_speed / 70.0)
        # Add some random noise
        congestion = max(0.0, min(1.0, congestion + random.uniform(-0.05, 0.05)))
        
        row = {
            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "intersection_id": intersection,
            "vehicle_count": vehicle_count,
            "avg_speed_kmh": avg_speed,
            "weather": weather,
            "temperature_c": temp,
            "is_weekend": is_weekend,
            "is_peak_hour": is_peak_hour,
            "accident_occurred": accident,
            "congestion_level": round(congestion, 3)
        }
        data.append(row)
        
        # Increment time by 15 minutes for each record overall (just to have sequential history)
        # Actually, let's step chronologically, rotating through intersections
        current_time += timedelta(minutes=15)
    
    df = pd.DataFrame(data)
    df.to_csv("yesil_traffic_history_dataset.csv", index=False)
    print(f"Successfully saved to 'yesil_traffic_history_dataset.csv'. Head:")
    print(df.head())

if __name__ == "__main__":
    generate_traffic_dataset()
