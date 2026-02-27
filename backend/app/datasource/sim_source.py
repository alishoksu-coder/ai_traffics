from datetime import timedelta
import math, random
from app.domain.models import Location, TrafficRecord
from app.datasource.base import DataSource

class SimSource(DataSource):
    def __init__(self, seed=42, center_lat=51.1694, center_lon=71.4491, n_points=20):
        self.rng = random.Random(seed)
        self.center_lat = center_lat
        self.center_lon = center_lon
        self.locations = self._make_locations(n_points)

    def _make_locations(self, n):
        locs = []
        for i in range(1, n+1):
            lat = self.center_lat + self.rng.uniform(-0.03, 0.03)
            lon = self.center_lon + self.rng.uniform(-0.03, 0.03)
            locs.append(Location(i, f"Point {i}", lat, lon))
        return locs

    def get_locations(self):
        return self.locations

    def _daily_pattern(self, minute_of_day: int) -> float:
        def g(x, mu, s): 
            return math.exp(-0.5*((x-mu)/s)**2)
        # morning ~ 08:00, evening ~ 18:00
        base = 0.18
        morning = g(minute_of_day, 8*60, 90)
        evening = g(minute_of_day, 18*60, 120)
        return base + 0.55*morning + 0.70*evening

    def get_records(self, start, end, step_minutes):
        t = start
        step = timedelta(minutes=step_minutes)

        # incidents: few random windows
        incidents = []
        total_minutes = int((end-start).total_seconds()//60)
        for _ in range(6):
            s = start + timedelta(minutes=self.rng.randint(0, max(0,total_minutes-1)))
            d = timedelta(minutes=self.rng.randint(15, 60))
            incidents.append((s, s+d))

        while t <= end:
            m = t.hour*60 + t.minute
            dow = t.weekday()
            weekend_factor = 0.75 if dow >= 5 else 1.0

            for loc in self.locations:
                loc_bias = (loc.id % 7) * 2.5
                noise = self.rng.gauss(0, 4.0)
                value = self._daily_pattern(m) * 60.0 * weekend_factor + loc_bias + noise

                for a,b in incidents:
                    if a <= t <= b:
                        value += 18 + self.rng.uniform(0, 8)

                value = max(0.0, min(100.0, value))
                yield TrafficRecord(t, loc.id, value)

            t += step
