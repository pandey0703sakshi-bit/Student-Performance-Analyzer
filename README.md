# Student Performance Analyzer

A Python-based academic analytics tool that reads student data, identifies at-risk students, generates visualizations, and outputs insights through a live web dashboard, color-coded Excel report, and structured text report.

---

## Features

- Automated at-risk student detection using multi-factor threshold logic
- Subject-wise performance analysis and class-wide trend identification
- 4 data visualizations — bar chart, heatmap, histogram, scatter plot
- Live interactive Streamlit web dashboard with real-time filters
- Color-coded Excel report with 3 sheets and embedded chart
- Structured text report with data-backed recommendations
- Upload any CSV or Excel dataset — not limited to sample data

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.11+ | Core language |
| Pandas | Data loading, cleaning, analysis |
| Matplotlib | Chart generation |
| Seaborn | Heatmap and styled visualizations |
| Streamlit | Interactive web dashboard |
| OpenPyXL | Excel report generation |

---

## Project Structure

```
student_analyzer/
│
├── data/
│   └── students.csv          # Raw student dataset (25 records)
│
├── charts/                   # Auto-generated chart images
│   ├── 01_subject_averages.png
│   ├── 02_heatmap.png
│   ├── 03_score_distribution.png
│   └── 04_attendance_vs_performance.png
│
├── analyzer.py               # Core analysis engine
├── excel_report.py           # Color-coded Excel report generator
├── dashboard.py              # Live Streamlit web dashboard
├── report.txt                # Auto-generated text report
├── student_report.xlsx       # Color-coded Excel output
└── README.md                 # This file
```

---

## Dataset Format

The tool expects a CSV or Excel file with these exact columns:

| Column | Description | Range |
|---|---|---|
| `Name` | Student full name | Text |
| `Math` | Math marks | 0 – 100 |
| `Science` | Science marks | 0 – 100 |
| `English` | English marks | 0 – 100 |
| `Attendance` | Attendance percentage | 0 – 100 |

A sample dataset with 25 students is included at `data/students.csv`.

---

## Setup

### 1. Clone or download the project

```bash
git clone https://github.com/yourusername/student-analyzer.git
cd student-analyzer
```

### 2. Install dependencies

```bash
pip3 install pandas matplotlib seaborn streamlit openpyxl
```

### 3. Confirm Python version

```bash
python3 --version
# Should print Python 3.11 or higher
```

---

## How to Run

### Run the core analyzer

Loads data, runs analysis, generates charts and saves `report.txt`:

```bash
python3 analyzer.py
```

**Output:**
- `charts/` — 4 PNG visualization files
- `report.txt` — full structured report printed to terminal and saved

---

### Run the Excel report generator

Generates a color-coded 3-sheet Excel file:

```bash
python3 excel_report.py
```

**Output:** `student_report.xlsx` with:
- Sheet 1 — Full student report (color-coded by status)
- Sheet 2 — Summary statistics + embedded bar chart
- Sheet 3 — At-risk students (focused red-themed view)

---

### Launch the Streamlit dashboard

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501` in your browser.

**Dashboard features:**
- Upload any CSV or Excel student dataset
- Filter by attendance range and student status in real time
- 6 live metric cards (class average, pass rate, correlation, etc.)
- 4 interactive charts updating with filters
- Color-coded student data table
- At-risk student alert section with recommendations
- Download filtered data or at-risk list as CSV

Press `Ctrl + C` in the terminal to stop the dashboard.

---

## At-Risk Detection Logic

A student is flagged **at-risk** if either condition is true:
- Average marks below **50**
- Attendance below **65%**

A student is a **top performer** if both conditions are true:
- Average marks at or above **80**
- Attendance at or above **85%**

All thresholds are defined in a single configuration block at the top of each file — change them once and the entire project updates automatically.

---

## Key Insights (Sample Dataset)

- Students with attendance ≥ 75% scored **~22 marks higher** on average than those below 75%
- Attendance-to-marks correlation coefficient: **0.98** (strong positive)
- Science was the weakest subject class-wide
- English was the strongest subject class-wide
- **6 out of 25 students** flagged as at-risk in the sample dataset
- **7 out of 25 students** identified as top performers

---

## Visualizations

| Chart | What it shows |
|---|---|
| Bar chart | Subject-wise class averages side by side |
| Heatmap | Every student's marks per subject (Red → Green scale) |
| Histogram | Distribution of student averages with threshold markers |
| Scatter plot | Attendance vs average marks — one dot per student |

---

## Future Improvements

- [ ] Machine learning risk prediction using scikit-learn (logistic regression)
- [ ] Semester-over-semester trend tracking
- [ ] Automated email alerts for counsellors when a student crosses risk thresholds
- [ ] PDF report export with charts embedded
- [ ] Multi-class support (analyze multiple classrooms at once)

---

## Author

**Sakshi Pandey**
Built as a portfolio project demonstrating end-to-end data analytics with Python.

---

## License

This project is open source and available under the [MIT License](LICENSE).
