from datetime import datetime, timedelta

def next_interval(old_interval: int, quality: int, ef: float) -> (int, float):
    """
    SM-2 核心計算：
    - quality < 3 → 重設為 1 天
    - quality >= 3 → 照公式遞增
    - quality == 5 且 old_interval 太小 → 降低 EF 成長，避免提早放棄複習
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

    # 更新 Ease Factor
    new_ef = ef + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))

    # 限制 EF 增長過快：若 interval 還小於 6，且 quality == 5，就放緩 EF 提升
    if quality == 5 and old_interval < 6:
        new_ef = ef + 0.05  # 輕微提升

    if new_ef < 1.3:
        new_ef = 1.3

    return new_interval, new_ef


def due_date_from_interval(interval: int) -> datetime:
    """計算下次複習的時間（現在 + interval 天）"""
    return datetime.utcnow() + timedelta(days=interval)


def sm2_review(last_interval: int, ease_factor: float, quality: int = 2) -> dict:
    """
    封裝 SM-2 流程：輸入上次間隔、EF 與回答品質，輸出新複習資料
    預設 quality = 2，代表不熟
    """
    interval, new_ef = next_interval(last_interval, quality, ease_factor)
    due_date = due_date_from_interval(interval)

    return {
        "interval": interval,
        "easeFactor": new_ef,
        "dueDate": due_date
    }
