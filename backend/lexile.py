import textstat

def approximate_lexile(text: str) -> int:
    """
    根據多種可讀性指標（Flesch–Kincaid、Gunning Fog、Dale–Chall、SMOG）
    計算文本的平均年級等級，並利用實證研究結果將年級等級映射到 Lexile 分數範圍。

    映射依據（ResearchGate 相關研究）:
    - Flesch–Kincaid 年級 5.9 約對應 850L
    - Flesch–Kincaid 年級 8.9 約對應 1010L

    線性映射參數:
      slope     = (1010 - 850) / (8.9 - 5.9) ≈ 53.33
      intercept = 850 - slope * 5.9 ≈ 535.3

    其他可讀性研究參考:
    - Readability of Written Materials for CKD Patients: A Systematic Review
      American Journal of Kidney Diseases, Feb 2015;65(6)
      DOI:10.1053/j.ajkd.2014.11.025 (Source: PubMed)

    注意: Lexile Framework 的原始算法為專利，本函式僅根據公開研究做近似映射。
    """
    # 1. 計算各指標年級等級
    fk_grade = textstat.flesch_kincaid_grade(text)
    fog_index = textstat.gunning_fog(text)
    dale_chall = textstat.dale_chall_readability_score(text)
    smog = textstat.smog_index(text)

    # 2. 計算平均年級等級
    avg_grade = (fk_grade + fog_index + dale_chall + smog) / 4.0

    # 3. 根據實證研究映射
    slope = (1010 - 850) / (8.9 - 5.9)  # 約 53.33
    intercept = 850 - slope * 5.9        # 約 535.3
    lexile = int(avg_grade * slope + intercept)

    # 4. 限制結果範圍
    lexile = max(200, min(2000, lexile))
    return lexile