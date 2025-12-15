📘 Financial Text Analyzer

Book: Rich Dad Poor Dad – Robert Kiyosaki

📌 Project Overview

This project is a Python-based Financial Text Analyzer created to analyze the book Rich Dad Poor Dad.
The main purpose of this project is to identify important financial ideas from the book and analyze them chapter-wise.

The system automatically reads the book text, detects chapters correctly, extracts meaningful financial sentences, and shows how financial concepts are distributed across different chapters using charts.

🎯 Objectives

Extract meaningful financial sentences from the book

Identify financial themes such as money, assets, investment, mindset, etc.

Map each sentence to its correct chapter

Perform chapter-wise and category-wise analysis

Store results in CSV file and SQLite database

Visualize insights using charts

🧠 Key Features

Correct chapter detection based on actual book headings

Sentence-level analysis using rule-based scoring

Parallel processing for faster execution

Category-wise financial analysis

Chapter-wise financial insight visualization

Clean and organized output structure

🛠️ Technologies Used

Python

Pandas – data processing

Matplotlib – data visualization

SQLite – database storage

Regex (re module) – text pattern matching

Multiprocessing – performance optimization

📂 Project Structure
Financial-Text-Analyzer/
│
├── text_analyzer.py
├── Rich-Dad-Poor-Dad.txt
├── output/
│   ├── csv/
│   │   ├── rich_dad_analysis_output.csv
│   │   └── results_hp.db
│   └── charts/
│       ├── category_scores_bar.png
│       └── chapter_trend_line.png
└── README.md

⚙️ How the System Works

Reads the book text line by line

Detects chapter headings using predefined patterns

Splits text into individual sentences

Assigns each sentence to its original chapter

Applies financial rules and scoring logic

Saves the extracted data into CSV and database

Generates charts for visual analysis

📊 Output Generated

The system generates four outputs:

1️⃣ CSV File

Contains all extracted financial sentences along with:

Category

Chapter number

Matched keyword

Score

📄 rich_dad_analysis_output.csv

2️⃣ SQLite Database

Stores the same analysis data in database format for structured access.

🗄 results_hp.db

3️⃣ Category-wise Bar Chart

Shows which financial themes (money, assets, mindset, etc.) appear most frequently in the book.

📊 category_scores_bar.png

4️⃣ Chapter-wise Line Chart

Shows how financial insights are distributed across chapters, helping identify chapters with more financial learning.

📈 chapter_trend_line.png
