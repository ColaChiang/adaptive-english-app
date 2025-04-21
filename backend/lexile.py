# lexile.py
import re
from collections import Counter

def lexile_score(text: str) -> int:
    # 1. 切句子，算平均每句多少單詞
    sentences = re.split(r'[.!?]+', text)
    word_counts = [len(s.split()) for s in sentences if s.strip()]
    avg_sentence_length = sum(word_counts) / max(len(word_counts), 1)

    # 2. 計算所有詞彙出現次數
    words = re.findall(r'\b\w+\b', text.lower())
    freq = Counter(words)

    # 3. 假設以下是一小段「高頻常見詞」，出現在 common_words 裡就視為「簡單詞」
    common_words = {"the","be","to","of","and","a","in","that","is","it","you","was"}
    uncommon = [w for w in words if w not in common_words]
    ratio_uncommon = len(uncommon) / max(len(words),1)

    # 4. 簡易計算公式：10×平均句長 + 50×不常見詞比例，再×10
    score = int((10 * avg_sentence_length + 50 * ratio_uncommon) * 10)
    return score