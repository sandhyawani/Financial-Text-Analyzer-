#Source Text: "Rich Dad Poor Dad" - Robert Kiyosaki

import re
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from textwrap import wrap
from multiprocessing import Pool, cpu_count
from collections import Counter
import os          
import io          
import contextlib  


# -------------------------- CONFIG -------------------------- #
FILE_PATH = "/content/drive/MyDrive/Rich-Dad-Poor-Dad.txt"
CSV_PATH = "/content/drive/MyDrive/rich_dad_analysis_output.csv"
DB_PATH = "/content/drive/MyDrive/results_hp.db"

#text report + chart folder paths
REPORT_PATH = "/content/drive/MyDrive/rich_dad_analysis_report.txt"
CHART_FOLDER = "/content/drive/MyDrive/rich_dad_charts"

# ensure chart folder exists
os.makedirs(CHART_FOLDER, exist_ok=True)


# -------------------------- CHAPTER METADATA -------------------------- #

CHAPTER_MARKERS = {
    0: "Introduction",
    1: "Chapter One",
    2: "Chapter Two",
    3: "Chapter Three",
    4: "Chapter Four",
    5: "Chapter Five",
    6: "Chapter Six",
    7: "Chapter Seven",
    8: "Chapter Eight",
    9: "Chapter Nine",
    10: "Final Thoughts",
}

CHAPTER_TITLES = {
    0: "Introduction – Rich Dad Poor Dad",
    1: "Lesson 1: The Rich Don’t Work for Money",
    2: "Lesson 2: Why Teach Financial Literacy?",
    3: "Lesson 3: Mind Your Own Business",
    4: "Lesson 4: The History of Taxes and the Power of Corporations",
    5: "Lesson 5: The Rich Invent Money",
    6: "Lesson 6: Work to Learn—Don’t Work for Money",
    7: "Overcoming Obstacles",
    8: "Getting Started",
    9: "Still Want More? Here Are Some To Do’s",
    10: "Final Thoughts",
}


# -------------------------- STAGE 1: READER -------------------------- #
def read_text(path):
    """Read raw text from file."""
    print("\n📘 Loading text...")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# -------------------------- STAGE 2: CLEAN + SPLIT -------------------------- #
def preprocess(text):
    """Clean extra whitespace and remove non-basic characters."""
    text = re.sub(r"\s+", " ", text)
    return re.sub(r"[^A-Za-z0-9.,!?\'\" ]+", "", text)


def split_sentences(text):
    """Split text into sentences based on punctuation."""
    return [s.strip() for s in re.split(r"(?<=[.!?]) +", text) if s.strip()]


def detect_chapters(sentences):
    """
    Detect chapter numbers for each sentence based on actual markers
    in the Rich Dad Poor Dad text.

    We look for "Introduction", "Chapter One", ..., "Chapter Nine",
    and "Final Thoughts" and map sentences to the most recent chapter.
    """
    chapters = []
    current_chapter = 0  # Start at Introduction by default

    for sentence in sentences:
        lower = sentence.lower()

        # Check if this sentence contains any chapter marker
        for chap_num, marker in CHAPTER_MARKERS.items():
            if marker.lower() in lower:
                # Move forward only (avoid jumping backwards on repeated headers)
                if chap_num > current_chapter:
                    current_chapter = chap_num
                break

        chapters.append(current_chapter)

    return chapters


# -------------------------- STAGE 3: RULES -------------------------- #
RULES = {
    "Money Terms": (r"\b(money|income|salary|cashflow|earn)\b", 2),
    "Assets vs Liabilities": (r"\b(asset|assets|liability|liabilities)\b", 3),
    "Rich vs Poor Mindset": (r"\brich\b.*\bpoor\b|\bpoor\b.*\brich\b", 4),
    "Investment Advice": (r"\binvest|investment|investor|return\b", 3),
    "Business & Education": (r"\bbusiness|education|teach|financial education|learning\b", 2),
    "Fear & Risk": (r"\bfear|risk|danger|mistake|failure\b", 2),
    "Mindset & Thinking": (r"\bmindset|thinking|belief|attitude\b", 3),
    "Advice Command": (r"^(Learn|Focus|Avoid|Start|Build|Invest)\b", 3),
    "Wealth Building": (r"\b(wealth|build|grow|create|accumulate)\b", 4),
}


def is_short_quote(sentence):
    """Return True if sentence has 10–25 words (good quote length)."""
    return 10 <= len(sentence.split()) <= 25


# -------------------------- STAGE 4: PARALLEL SCORING -------------------------- #
def process_sentence(args):
    """
    Apply all rules to a single sentence.
    Returns a list of rows [Category, Chapter, Sentence No, Matched Keyword, Sentence, Score].
    """
    idx, sentence, chapter = args
    rows = []

    # Short-quote logic
    if is_short_quote(sentence):
        rows.append(["Short Quote (10–25 words)", chapter, idx, "length_match", sentence, 1])

    # Regex-based rules
    for rule_name, (pattern, score) in RULES.items():
        match = re.search(pattern, sentence, re.IGNORECASE)
        if match:
            rows.append([rule_name, chapter, idx, match.group(0), sentence, score])

    return rows


def analyze(sentences, chapters):
    """Run the rule engine in parallel over all sentences."""
    print("\n⚙ Applying rules using parallel processing…")

    task_data = [(i, sentences[i], chapters[i]) for i in range(len(sentences))]

    with Pool(cpu_count()) as pool:
        results = pool.map(process_sentence, task_data)

    flat = [item for sublist in results for item in sublist]

    df = pd.DataFrame(flat, columns=[
        "Category", "Chapter", "Sentence No", "Matched Keyword", "Sentence", "Score"
    ])

    print(f"✓ Completed: {len(df)} matched items found.")
    return df


# -------------------------- STAGE 5: STORAGE -------------------------- #
def save_results(df):
    """Save results to CSV and SQLite database."""
    df.to_csv(CSV_PATH, index=False)

    conn = sqlite3.connect(DB_PATH)
    df.to_sql("analysis_results", conn, if_exists="replace", index=False)
    conn.close()

    print("\n💾 Saved:")
    print(f"   ✔ CSV → {CSV_PATH}")
    print(f"   ✔ DB  → {DB_PATH}")


# -------------------------- STAGE 6: VISUALISATION -------------------------- #
def visualize(df, cleaned_text):
    """Create bar, pie, line, and keyword frequency charts."""
    print("\n📊 Creating charts...\n")

    chapter_scores = df.groupby("Chapter")["Score"].sum()
    category_scores = df.groupby("Category")["Score"].sum()

    # --- BAR CHART: Category scores ---
    plt.figure(figsize=(15, 6))
    ax = category_scores.sort_values().plot(kind="barh", color="#5271FF")
    ax.set_title("Score by Rule Category", fontsize=15)
    ax.set_yticklabels(['\n'.join(wrap(label.get_text(), 25)) for label in ax.get_yticklabels()])
    plt.tight_layout()
    plt.savefig(f"{CHART_FOLDER}/category_scores_bar.png")  # ADDED
    plt.show()

    # --- PIE CHART: Category share ---
    colors = plt.cm.Set3(range(len(category_scores)))
    plt.figure(figsize=(12, 9))

    wedges, texts, autotexts = plt.pie(
        category_scores,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors,
        textprops={'fontsize': 11}
    )

    for t in autotexts:
        t.set_fontweight("bold")

    legend_labels = [
        f"{name}  ({category_scores[name]} pts | {category_scores[name] / category_scores.sum()*100:.1f}%)"
        for name in category_scores.index
    ]

    plt.legend(
        wedges, legend_labels,
        title="Categories (Score + Contribution)",
        bbox_to_anchor=(1, 0.5),
        fontsize=10
    )

    plt.title("Distribution of Financial Themes", fontsize=16)
    plt.tight_layout()
    plt.savefig(f"{CHART_FOLDER}/category_distribution_pie.png") 
    plt.show()

    # --- LINE CHART: Chapter score trend ---
    plt.figure(figsize=(10, 5))
    chapter_scores.plot(marker="o", linewidth=3, color="#FF4E6A")
    plt.title("Financial Insight Density Per Chapter", fontsize=15)
    plt.xlabel("Chapter")
    plt.ylabel("Score Total")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"{CHART_FOLDER}/chapter_trend_line.png")  
    plt.show()

    # --- FINANCIAL KEYWORD FREQUENCY ---
    keywords = [
        'money', 'asset', 'assets', 'liability', 'income', 'investment', 'invest',
        'cashflow', 'business', 'debt', 'financial', 'freedom', 'rich', 'poor'
    ]

    freq = Counter([w for w in cleaned_text.lower().split() if w in keywords])

    if freq:
        labels, counts = zip(*freq.most_common(10))
        plt.figure(figsize=(12, 5))
        plt.bar(labels, counts, color="#2ECC71")
        plt.title("Most Common Financial Keywords", fontsize=15)
        plt.tight_layout()
        plt.savefig(f"{CHART_FOLDER}/keyword_frequency.png")  
        plt.show()

    print(f"\n🖼 Charts saved in Google Drive folder: {CHART_FOLDER}\n")


# -------------------------- STAGE 7: REPORT -------------------------- #
def final_report(df):
    """
    Print category-wise summary + chapter-wise quotes.
    Shows chapter number and chapter title for each quote group.
    """
    print("\n📝 FINAL REPORT")
    print("--------------------------------------------------------")
    print(f"Total extracted meaningful sentences: {len(df)}\n")

    category_scores = df.groupby("Category")["Score"].sum().sort_values(ascending=False)
    print("📌 Category Score Summary:")
    print(category_scores, "\n")

    print("\n🔍 Key Quotes (Up to 5 per Category per Chapter):\n")

    for category in df["Category"].unique():
        print(f"\n▶ {category}")
        print("-" * (len(category) + 4))

        # For each chapter where this category appears
        category_subset = df[df["Category"] == category]
        for chap_id in sorted(category_subset["Chapter"].unique()):
            chap_title = CHAPTER_TITLES.get(chap_id, "Unknown Chapter")

            print(f"\n   📚 Chapter {chap_id}: {chap_title}")

            chapter_quotes = (
                category_subset[category_subset["Chapter"] == chap_id]
                .sort_values(by="Score", ascending=False)
                .drop_duplicates(subset=["Sentence"])
                .head(5)
            )

            for _, row in chapter_quotes.iterrows():
                print(f"\n      ▪ Sentence {row['Sentence No']}")
                print(f"        \"{row['Sentence']}\"")

    print("\n--------------------------------------------------------")
    print("End of analysis. Scroll up for charts and details.\n")


# -------------------------- EXTRA: TOP 5 BEST SENTENCES -------------------------- #
def print_top_best_sentences(df, n=5):
    """Print top N sentences globally with full detail (category, score, chapter, keyword)."""
    print("\n============== TOP 5 BEST SENTENCES (BY SCORE) ==============\n")

    top = df.sort_values(by="Score", ascending=False).head(n)

    for _, row in top.iterrows():
        chap_title = CHAPTER_TITLES.get(row["Chapter"], "Unknown Chapter")
        print(f"Category     : {row['Category']}")
        print(f"Score        : {row['Score']}")
        print(f"Chapter      : {row['Chapter']} ({chap_title})")
        print(f"Sentence No  : {row['Sentence No']}")
        print(f"Keyword Hit  : {row['Matched Keyword']}")
        print(f"Sentence     : {row['Sentence']}")
        print("-" * 60)


# -------------------------- SAVE CONSOLE REPORT -------------------------- #
def save_console_report_to_drive(text):
    """Save the final printed report to a text file in Google Drive."""
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"\n📝 Full console report also saved to: {REPORT_PATH}\n")


# -------------------------- MAIN PIPELINE -------------------------- #
def run():
    print("\n🚀 Running Full Text Analysis Pipeline...")

    # Reader
    text = read_text(FILE_PATH)

    # Cleaning + splitting
    cleaned = preprocess(text)
    sentences = split_sentences(cleaned)
    chapters = detect_chapters(sentences)

    print(f"📌 Total Sentences: {len(sentences)}")

    # Rule engine + scoring
    df = analyze(sentences, chapters)

    # Storage
    save_results(df)

    # Visualisations (also saved in Drive)
    visualize(df, cleaned)

    # Final report + top 5 sentences
    # Capture console output, print it, and save to Drive
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        final_report(df)
        print_top_best_sentences(df, n=5)

    report_text = buffer.getvalue()
    print(report_text)                    # show in console
    save_console_report_to_drive(report_text)  # save in Drive

    print("\n🎉 FINISHED — All Requirements Completed Successfully.\n")


# -------------------------- EXECUTION -------------------------- #
if __name__ == "__main__":
    run()
