# Financial-Text-Analyzer-
A Python-based financial text analysis project that processes the book *Rich Dad Poor Dad* using rule-based NLP and parallel processing. The system detects key financial themes, scores sentences, generates data visualizations, and exports results into CSV, SQLite, and a formatted summary report.

This program automatically:

- Reads the complete book text
- Cleans and tokenizes the text into sentences
- Detects chapters dynamically using text patterns
- Applies NLP rules to identify financial themes
- Scores sentences based on keyword and semantic relevance
- Stores results in **CSV and SQLite database**
- Generates multiple visual charts (Bar, Pie, Line, Keyword Frequency)
- Produces a final structured summary including Top 5 Best Sentences

 Techniques Used
This project uses **Rule-based NLP**, including:

| NLP Technique | Example in Code |
|--------------|-------------------|
| Text Preprocessing | Removing symbols, extra spaces |
| Tokenization | Splitting text into sentences |
| Keyword & Pattern Recognition | Regex-based rule matching |
| Semantic Scoring | Assigning weights based on meaning |
| Information Extraction | Categorizing quotes into financial themes |
| Summarization | Generating top insights and best sentences |

Example rule:

```python
"Investment Advice": (r"\binvest|investment|investor|return\b", 3)
