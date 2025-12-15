# Project: Financial Text Analyzer
# Book: Rich Dad Poor Dad – Robert Kiyosaki
# Purpose: Chapter-wise financial insight analysis

import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count
import os


# ------------------------------
# Output folders
# ------------------------------
BASE_OUTPUT_DIR = "output"
CSV_FOLDER = os.path.join(BASE_OUTPUT_DIR, "csv")
CHART_FOLDER = os.path.join(BASE_OUTPUT_DIR, "charts")

os.makedirs(CSV_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)


# ------------------------------
# File paths
# ------------------------------
FILE_PATH = "Rich-Dad-Poor-Dad.txt"
CSV_PATH = os.path.join(CSV_FOLDER, "rich_dad_analysis_output.csv")
DB_PATH = os.path.join(CSV_FOLDER, "results_hp.db")


# ------------------------------
# Chapter info
# ------------------------------
CHAPTER_TITLES = {
    0: "Introduction",
    1: "Lesson 1: The Rich Don’t Work for Money",
    2: "Lesson 2: Why Teach Financial Literacy?",
    3: "Lesson 3: Mind Your Own Business",
    4: "Lesson 4: History of Taxes & Corporations",
    5: "Lesson 5: The Rich Invent Money",
    6: "Lesson 6: Work to Learn",
    7: "Overcoming Obstacles",
    8: "Getting Started",
    9: "Still Want More?",
    10: "Final Thoughts",
}

CHAPTER_PATTERNS = {
    0: r"^Introduction$",
    1: r"^Chapter One$",
    2: r"^Chapter Two$",
    3: r"^Chapter Three$",
    4: r"^Chapter Four$",
    5: r"^Chapter Five$",
    6: r"^Chapter Six$",
    7: r"^Chapter Seven$",
    8: r"^Chapter Eight$",
    9: r"^Chapter Nine$",
    10: r"^Final Thoughts$",
}


# ------------------------------
# Read text
# ------------------------------
def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()


# ------------------------------
# Cleaning
# ------------------------------
def clean_line(text):
    text = re.sub(r"\s+", " ", text.strip())
    return re.sub(r"[^A-Za-z0-9.,!?\'\" ]+", "", text)


# ------------------------------
# Detect chapter per line
# ------------------------------
def detect_chapters_per_line(lines):
    chapters = []
    current = 0

    patterns = {
        chap: re.compile(pat, re.IGNORECASE)
        for chap, pat in CHAPTER_PATTERNS.items()
    }

    for line in lines:
        cleaned = clean_line(line)

        for chap, pat in patterns.items():
            if pat.match(cleaned):
                current = chap
                break

        chapters.append(current)

    return chapters


# ------------------------------
# Split sentences WITH chapter mapping
# ------------------------------
def split_sentences_with_chapters(lines):
    sentences = []
    sentence_chapters = []

    chapters_per_line = detect_chapters_per_line(lines)

    for line, chap in zip(lines, chapters_per_line):
        cleaned = clean_line(line)
        if cleaned:
            parts = re.split(r"(?<=[.!?]) +", cleaned)
            for s in parts:
                s = s.strip()
                if s:
                    sentences.append(s)
                    sentence_chapters.append(chap)

    return sentences, sentence_chapters


# ------------------------------
# Financial rules
# ------------------------------
RULES = {
    "Money Terms": (r"\b(money|income|salary|cashflow|earn)\b", 2),
    "Assets vs Liabilities": (r"\b(asset|assets|liability|liabilities)\b", 3),
    "Rich vs Poor Mindset": (r"\brich\b.*\bpoor\b|\bpoor\b.*\brich\b", 4),
    "Investment Advice": (r"\binvest|investment|investor|return\b", 3),
    "Business & Education": (r"\bbusiness|education|teach|learning\b", 2),
    "Fear & Risk": (r"\bfear|risk|mistake|failure\b", 2),
    "Mindset": (r"\bmindset|thinking|belief|attitude\b", 3),
    "Wealth Building": (r"\b(wealth|build|grow|create)\b", 4),
}


def is_short_quote(s):
    return 10 <= len(s.split()) <= 25


# ------------------------------
# Sentence processing
# ------------------------------
def process_sentence(args):
    idx, sentence, chapter = args
    rows = []

    if is_short_quote(sentence):
        rows.append(["Short Quote", chapter, idx, "length", sentence, 0.3])

    for name, (pattern, score) in RULES.items():
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            rows.append([name, chapter, idx, match.group(), sentence, score])

    return rows


def analyze(sentences, chapters):
    tasks = [(i, sentences[i], chapters[i]) for i in range(len(sentences))]

    with Pool(cpu_count()) as pool:
        results = pool.map(process_sentence, tasks)

    data = [item for sub in results for item in sub]

    return pd.DataFrame(
        data,
        columns=[
            "Category",
            "Chapter",
            "Sentence No",
            "Matched Keyword",
            "Sentence",
            "Score",
        ],
    )


# ------------------------------
# Charts
# ------------------------------
def visualize(df):
    category_scores = df.groupby("Category")["Score"].sum().sort_values()
    chapter_scores = df.groupby("Chapter")["Score"].sum()

    # Bar chart
    plt.figure(figsize=(14, 6))
    category_scores.plot(kind="barh")
    plt.title("Score by Rule Category")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "category_scores_bar.png"))
    plt.close()

    # Line chart
    plt.figure(figsize=(12, 6))
    chapter_scores.plot(marker="o", linewidth=2)
    plt.xticks(
        range(len(CHAPTER_TITLES)),
        [CHAPTER_TITLES[i] for i in range(len(CHAPTER_TITLES))],
        rotation=30,
        ha="right",
    )
    plt.title("Financial Insight Density Per Chapter")
    plt.ylabel("Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "chapter_trend_line.png"))
    plt.close()


# ------------------------------
# Main
# ------------------------------
def run():
    lines = read_text(FILE_PATH)

    sentences, chapters = split_sentences_with_chapters(lines)

    df = analyze(sentences, chapters)

    df.to_csv(CSV_PATH, index=False)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("analysis_results", conn, if_exists="replace", index=False)
    conn.close()

    visualize(df)

    print("Analysis completed successfully")


if __name__ == "__main__":
    run()
