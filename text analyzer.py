import re
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

#create output directories
BASE_OUTPUT_DIR = "output"
CSV_FOLDER = os.path.join(BASE_OUTPUT_DIR, "csv")
CHART_FOLDER = os.path.join(BASE_OUTPUT_DIR, "charts")

os.makedirs(CSV_FOLDER, exist_ok=True)
os.makedirs(CHART_FOLDER, exist_ok=True)

#file paths
FILE_PATH = "Rich-Dad-Poor-Dad.txt"
CSV_PATH = os.path.join(CSV_FOLDER, "rich_dad_analysis_output.csv")
DB_PATH = os.path.join(CSV_FOLDER, "results_hp.db")

#chap info
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

# Read text
def read_text(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read().splitlines()

# Cleaning - Removes extra spaces and unwanted characters.
def clean_line(text):
    text = re.sub(r"\s+", " ", text.strip())
    return re.sub(r"[^A-Za-z0-9.,!?\'\" ]+", "", text)

#Skips content like ISBN or copyright text.
def is_noise(text):
    return any(w in text.lower() for w in ["copyright", "isbn", "publisher", "cashflow"])

#Converts text to lowercase and removes extra spaces
def normalize(text):
    return re.sub(r"\s+", " ", text.lower().strip())

#Chapter detection
def detect_chapters(lines):
    current = 0
    chapters = []
    patterns = {k: re.compile(v, re.I) for k, v in CHAPTER_PATTERNS.items()}

    for line in lines:
        cleaned = clean_line(line)
        for chap, pat in patterns.items():
            if pat.match(cleaned):
                current = chap
                break
        chapters.append(current)

    return chapters

# Splits text into individual sentences
def split_sentences(lines):
    sentences, chapters = [], []
    chapter_map = detect_chapters(lines)

    for line, chap in zip(lines, chapter_map):
        cleaned = clean_line(line)
        if not cleaned or is_noise(cleaned):
            continue

        for s in re.split(r"(?<=[.!?])\s+", cleaned):
            if len(s.split()) >= 8:
                sentences.append(s)
                chapters.append(chap)

    return sentences, chapters

#linancial keyword rules
FINANCIAL_RULES = {
    "Money Concept": (r"\b(money|income|salary|cashflow)\b", 2),
    "Assets vs Liabilities": (r"\b(asset|assets|liability|liabilities)\b", 3),
    "Investment Advice": (r"\b(invest|investment|return)\b", 3),
    "Wealth Creation": (r"\b(wealth|build|grow|create)\b", 4),
}
#lesson explanation patterns
LESSON_PATTERNS = {
    "Rich vs Poor Comparison": r"\b(rich|poor).*(work|think|spend|save)\b",
    "Cause–Effect Explanation": r"\b(because|therefore|leads to|results in)\b",
    "Advice / Principle": r"\b(should|must|need to|have to)\b",
    "Definition / Explanation": r"\b(means that|defined as|refers to)\b",
}

#financial keywords list
FIN_KEYWORDS = [
    "money", "asset", "liability", "income",
    "investment", "wealth", "business", "rich", "poor"
]

#Sentence analysis function
def process_sentence(args):
    idx, sentence, chapter = args
    rows = []

    for name, (pat, score) in FINANCIAL_RULES.items():
        if re.search(pat, sentence, re.I):
            rows.append([name, chapter, idx, "keyword", sentence, score])

    for lesson, pat in LESSON_PATTERNS.items():
        if re.search(pat, sentence, re.I):
            rows.append([
                "Financial Lesson Explanation",
                chapter, idx, lesson, sentence, 5
            ])

    return rows

#parallel sentence analysis
def analyze(sentences, chapters):
    with Pool(cpu_count()) as pool:
        results = pool.map(
            process_sentence,
            [(i, sentences[i], chapters[i]) for i in range(len(sentences))]
        )

    data = [r for sub in results for r in sub]

    df = pd.DataFrame(
        data,
        columns=["Category", "Chapter", "Sentence No",
                 "Matched Pattern", "Sentence", "Score"]
    )

    df["Norm"] = df["Sentence"].apply(normalize)
    df.drop_duplicates(subset=["Category", "Chapter", "Norm"], inplace=True)
    df.drop(columns="Norm", inplace=True)

    return df

#data visualization
def visualize(df):

    #Category Score Bar Chart
    cat_scores = df.groupby("Category")["Score"].sum().sort_values()
    plt.figure(figsize=(12, 6))
    cat_scores.plot(kind="barh")
    plt.title("Financial Insight Score by Category")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "category_score_bar.png"))
    plt.close()

    #Category Distribution Pie Chart
    plt.figure(figsize=(10, 10))
    plt.pie(cat_scores, autopct="%1.1f%%", startangle=90)
    plt.legend(cat_scores.index, bbox_to_anchor=(1, 0.5))
    plt.title("Distribution of Financial Lessons")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "category_distribution_pie.png"))
    plt.close()

    #Chapter-wise Lesson Density
    chap_scores = df.groupby("Chapter")["Score"].sum()
    plt.figure(figsize=(12, 6))
    chap_scores.plot(marker="o")
    plt.xticks(
        range(len(CHAPTER_TITLES)),
        [CHAPTER_TITLES[i] for i in range(len(CHAPTER_TITLES))],
        rotation=30, ha="right"
    )
    plt.title("Financial Lesson Density per Chapter")
    plt.ylabel("Score")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "chapter_trend_line.png"))
    plt.close()

    #  Lesson Explanation Pattern Frequency
    lesson_df = df[df["Category"] == "Financial Lesson Explanation"]
    pattern_counts = lesson_df["Matched Pattern"].value_counts()

    plt.figure(figsize=(12, 6))
    pattern_counts.plot(kind="bar")
    plt.title("How Financial Lessons Are Explained")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(os.path.join(CHART_FOLDER, "lesson_explanation_patterns.png"))
    plt.close()

    # Financial Keyword Frequency 
    text = " ".join(lesson_df["Sentence"]).lower()
    words = re.findall(r"\b\w+\b", text)
    freq = {w: words.count(w) for w in FIN_KEYWORDS if w in words}

    if freq:
        pd.Series(freq).sort_values(ascending=False).plot(kind="bar", figsize=(12, 6))
        plt.title("Financial Keyword Frequency in Lesson Explanations")
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(os.path.join(CHART_FOLDER, "financial_keyword_frequency.png"))
        plt.close()

#execution
def run():
    lines = read_text(FILE_PATH)
    sentences, chapters = split_sentences(lines)
    df = analyze(sentences, chapters)

    df.to_csv(CSV_PATH, index=False)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("analysis_results", conn, if_exists="replace", index=False)
    conn.close()

    visualize(df)
    print("Analysis completed successfully")

if __name__ == "__main__":
    run()
