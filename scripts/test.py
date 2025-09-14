import math
from datetime import datetime

def recency_weight(timestamp: datetime, now: datetime | None = None, half_life_years: float = 0.5) -> float:
    now = now or datetime.utcnow()
    t_years = (now - timestamp).days / 365.25
    lam = math.log(2) / half_life_years
    return math.exp(-lam * t_years)

print(recency_weight(datetime(2025, 1, 1), datetime(2025, 9, 12), 0.5))