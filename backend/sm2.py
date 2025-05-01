# backend/sm2.py

from datetime import datetime, timedelta

def next_interval(old_interval: int, quality: int, ef: float) -> (int, float):
    """
    SM-2 核心：
    - old_interval: 上一次間隔（天）
    - quality: 回答品質 0~5
    - ef: 現有易度因子（ease factor）
    回傳 (new_interval, new_ef)
    """
    if quality < 3:
        new_interval = 1
    else:
        if old_interval == 0:
            new_interval = 1
        elif old_interval == 1:
            new_interval = 6
        else:
            new_interval = int(old_interval * ef)
    # 更新 EF
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    if new_ef < 1.3:
        new_ef = 1.3
    return new_interval, new_ef

def due_date_from_interval(interval: int) -> datetime:
    """給定天數，回傳下次複習的 datetime."""
    return datetime.utcnow() + timedelta(days=interval)