# 🤖 Telco Customer Churn — Autonomous Data Analyst Agent

> **Ask a question in plain English. Get a full analysis, insights, and charts — automatically.**

---

## 📌 What Is This Project?

This is an **AI-powered data analysis tool** built in Python that works like a smart analyst sitting beside you.

You give it a dataset (a telecom company's customer records) and type a question in plain English — for example:

> *"Why are customers leaving? Which group churns the most?"*

The tool reads your question, figures out what you're asking, analyses the data, prints a structured report in the terminal, and saves **three professional charts** to your computer — all without you writing a single line of code or clicking anything.

---

## 🧩 The Business Problem It Solves

A telecom company has **7,043 customer records** with information like:
- What type of contract they are on (Monthly, 1-Year, 2-Year)
- How long they've been a customer (tenure)
- How much they pay per month
- Whether they eventually left the company (churned) or stayed

**Business questions this tool answers:**

| You ask... | The tool figures out... |
|---|---|
| Which customers contribute the most revenue? | Revenue breakdown by contract type and tenure |
| Which group of customers is leaving us the most? | Churn rate across any segment you choose |
| Do customers who leave pay more or less? | Monthly charges comparison: churned vs retained |
| What is the single biggest reason customers leave? | Ranks all factors by their impact on churn |

---

## ⚙️ How It Works — Step by Step

### Step 1 — You Type a Question

When you run the script, the very first thing it does is ask **you** what you want to know:

```
Enter the type of analysis or insights you want from the dataset:
> Analyze churn across contract types
```

You type anything in plain English. The tool handles the rest.

---

### Step 2 — It Reads and Cleans the Data Automatically

Before any analysis, the tool silently fixes common data problems:

- **Column names** are cleaned up (e.g. `"Total Charges"` → `total_charges`) so the code can work with them reliably
- **Blank values** in the `Total Charges` column (11 brand-new customers with no bills yet) are automatically converted to `$0` — the correct answer — instead of crashing
- **Duplicate records** are removed defensively
- A new **Tenure Group** column is created by bucketing raw tenure months into readable ranges: `0–12 mo`, `13–24 mo`, `25–48 mo`, `49–72 mo`

No manual data preparation is needed.

---

### Step 3 — It Understands Your Question (Query Interpreter)

This is the brain of the project.

The tool reads your question and identifies two things:

1. **What you want to measure** — revenue/charges, churn, or a comparison of both
2. **How you want to slice the data** — by contract type, payment method, tenure, internet service, senior status, gender, etc.

It does this using a keyword-matching approach:

```
"Analyze churn across payment methods"
        ↓
Detects: "churn" → analysis type = churn rate
Detects: "payment" → dimension = payment_method column
        ↓
Runs: Churn Rate Analysis grouped by Payment Method
```

It maps over **15 different dimensions** from the dataset automatically. If your question is unclear or empty, it safely falls back to the default report rather than crashing.

---

### Step 4 — It Runs One of Four Analysis Modes

Based on what it understood from your question, it picks the right analysis:

| Mode | When it activates | What it calculates |
|---|---|---|
| **Charges by Segment** | You ask about revenue, top/bottom contributors | Total revenue, average, % share per segment |
| **Churn by Segment** | You ask about churn, leaving, attrition | Churn rate per segment vs overall baseline |
| **Charges vs Churn** | You mention both charges AND churn | Average monthly bill: churned vs retained customers |
| **Key Factors** | You ask about drivers, factors, or imbalances | Ranks every dimension by how much its churn rate varies |

---

### Step 5 — It Prints a Structured Report

Every mode prints a clean, readable report directly in the terminal:

```
======================================================================
TELCO CHURN ANALYSIS  -  by CONTRACT
======================================================================
Customers         : 7,043
Overall churn rate: 26.5%

--- Churn rate by Contract ---
                  churn_rate   customers   churned
Month-to-month        42.7%        3,875     1,655   ← highest risk
One year              11.3%        1,473       166
Two year               2.8%        1,695        48   ← safest group

Highest churn : Month-to-month  (42.7%)
Lowest churn  : Two year  (2.8%)
```

---

### Step 6 — It Saves Three Professional Charts

Every analysis saves exactly **three charts** to an `output/` folder automatically created next to the script:

| Chart | What it shows |
|---|---|
| **Bar Chart** | Side-by-side comparison of all segments |
| **Pie Chart** | Proportional share (revenue or churn) per segment |
| **Line Chart** | Trend over customer lifetime (charges or churn vs tenure) |

Charts have clean titles, labelled axes, dollar/percentage formatting, and consistent colour coding — ready to drop into a presentation or report.

---

## 📊 Key Findings From the Dataset

Here is what the tool discovered when run against the Telco dataset:

### 💰 Revenue Contribution
- **Two-year contracts** generate **39.1% of all revenue** ($6.28M) despite being only 24% of customers
- Month-to-month customers are the **largest group (55%)** but contribute the lowest revenue per person ($1,369 average vs $3,707 for two-year)
- Customers in their **last year of tenure (49–72 months)** generate **65% of all revenue** — the company's most valuable group

### 📉 Churn Risk
- **Month-to-month customers churn at 42.7%** — nearly 15× higher than two-year customers (2.8%)
- **Electronic check users churn at 45.3%** — the highest of any payment method
- **Fiber optic internet users churn at 41.9%** — a hidden risk segment
- **Senior citizens churn at 41.7%** vs 23.6% for non-seniors
- Customers who churn actually **pay $13.18/month more** than those who stay — they are on premium plans but still leave

### 🔑 Strongest Churn Drivers (ranked)
| Rank | Factor | Churn Gap |
|---|---|---|
| 1 | Contract Type | 39.9 percentage points |
| 2 | Tenure Group | 37.9 percentage points |
| 3 | Internet Service | 34.5 percentage points |
| 4 | Payment Method | 30.0 percentage points |
| 5 | Dependents | 26.0 percentage points |

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **pandas** | Data loading, cleaning, grouping, and aggregation |
| **matplotlib** | Chart generation (bar, pie, line) |
| **openpyxl** | Reading the Excel (.xlsx) dataset |
| **pathlib** | Cross-platform file path handling (works on Windows, Mac, Linux) |

No external APIs, no cloud services, no dashboards — runs entirely on your local machine.

---

## 🚀 How to Run It

### 1. Install dependencies
```bash
pip install pandas matplotlib openpyxl
```

### 2. Set your dataset path
Open `telco_churn_analysis.py` and update line 22:
```python
DATA_PATH = Path(r"C:\Your\Path\To\Telco_customer_churn.xlsx")
```

### 3. Run the script
```bash
python telco_churn_analysis.py
```

### 4. Type your question and press Enter
```
Enter the type of analysis or insights you want from the dataset:
> Compare churn across payment methods
```

### 5. Check your results
- Report prints in the terminal
- Charts saved to: `output/` folder (created automatically)

---

## 💬 Example Queries You Can Ask

```
Analyze churn across contract types
Compare churn across payment methods
Explain relationship between tenure and churn
Evaluate monthly charges vs churn
Identify top and bottom segments by total charges
Analyze impact of internet service on churn
Compare senior vs non-senior churn behavior
Identify key factors influencing churn
```

*(Press Enter with no text for the default revenue-by-contract report)*

---

## 📁 Project Structure

```
📦 Project Folder
├── telco_churn_analysis.py       ← Main script (run this)
├── Telco_customer_churn.xlsx     ← Dataset (place here)
└── output/                       ← Auto-created on first run
    ├── bar_chart_*.png
    ├── pie_chart_*.png
    └── line_chart_*.png
```

---

## 🧠 What Makes This Project Interesting (For Recruiters)

| Skill Demonstrated | How It Shows Up In This Project |
|---|---|
| **Data Cleaning** | Automatically handles blank values, type mismatches, and duplicates |
| **Exploratory Data Analysis** | Segments, aggregates, and compares data across multiple dimensions |
| **Natural Language Processing (basic NLP)** | Keyword-based query parser that maps plain English to dataset columns |
| **Data Visualisation** | Generates 3 production-quality charts per analysis using matplotlib |
| **Software Design** | Four modular analysis modes, shared helpers, clean dispatch architecture |
| **Cross-platform Engineering** | Raw string paths, ASCII-safe output, `pathlib` for OS portability |
| **Business Thinking** | Findings are framed as actionable insights, not just numbers |

---

## 📌 Dataset

**Source:** IBM Telco Customer Churn Dataset (publicly available)
**Records:** 7,043 customers
**Columns:** 33 features including demographics, services, contract details, billing, and churn status

---

## 👤 Author

Built as a demonstration of autonomous data analysis — combining data engineering, analysis, visualisation, and basic NLP into a single, self-contained Python script that any business user can run with one command.

---

*Feel free to fork, extend, or adapt this project. Pull requests welcome.*
