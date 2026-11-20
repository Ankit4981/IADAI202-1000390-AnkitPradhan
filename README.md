# LogiSight Analytics — Last-Mile Delivery Performance Dashboard

**CRS Artificial Intelligence — Formative Assessment-2 (FA-2)**
*Mathematics for AI-II: Analyzing Last-Mile Delivery Data for Performance Insights*

---

## Academic & Institutional Metadata

- **Student Name:** Ankit Pradhan
- **Roll Number:** 1000390
- **Course:** CRS Artificial Intelligence — Mathematics for AI-II
- **Assessment:** Formative Assessment-2 (FA-2: Dashboarding & Deployment)
- **Organization:** LogiSight Analytics Pvt. Ltd.
- **Academic Partners:** Westcliff Academic Partner (WACP) & Viraj International

---

## 1. Project Overview

This application transforms the FA-1 design storyboard into a fully functional, interactive logistics analytics dashboard built with **Python**, **Streamlit**, **Pandas**, and **Plotly**.

The platform operates as a modern business intelligence product designed for logistics operations managers, with live drill-down capabilities across weather conditions, traffic density, vehicle fleet modalities, delivery agent cohorts, geographic regions, and product categories.

Every metric, card, table, and visualization is computed dynamically from the supplied delivery dataset (43,739 records). No values are hardcoded, fabricated, or copied from reference images.

---

## 2. Five Website Sections

The application is organized into five dedicated analytical sections, each accessible via the sidebar navigation:

### Section 1 — Delivery Analysis
- **Delay Analyzer** (Grouped Bar Chart): Weather × Traffic impact on delivery time.
- **Vehicle Comparison** (Bar Chart): Average delivery time by vehicle modality (Van, Scooter, Motorcycle, Bicycle).
- **Traffic & Weather Interaction Matrix**: Styled pivot table showing mean delivery time per weather–traffic combination.
- **Fleet Modality Performance Breakdown**: Summary table with average time, order count, late rate, and delta vs. fastest vehicle.

### Section 2 — Agent Performance
- **Agent Performance Scatter Plot**: Rating vs. Delivery Time colored by age cohort (< 25, 25–40, 40+) with OLS trendline.
- **Workforce Cohort Statistics Table**: Orders, average rating, average delivery time, and late rate per age group.
- **Data Quality Note**: Flags 53 records with Agent_Rating = 6.0 and 54 records with missing ratings.

### Section 3 — Regional & Category
- **Area Heatmap**: Average Delivery Time by Area × Traffic with teal intensity scale.
- **Category Boxplot**: Distribution of delivery times across all 16 product categories showing median, quartiles, whiskers, and outliers.
- **Auto-Generated Insights**: Dynamically computed observations about worst-performing areas, traffic conditions, and categories.

### Section 4 — Data Preparation
- **Late Delivery Mathematical Formulation**: Formula, threshold calculation using sample std (ddof=1), and all computed statistics.
- **Data Cleaning Audit Trail**: Dynamically computed counts for raw records, missing values, spelling corrections, and suspicious ratings.
- **Methodology Notes**: Documentation of every cleaning step and analytical decision.
- **Cleaned Dataset Preview**: Interactive Streamlit dataframe with 12 key columns.

### Section 5 — About Project
- **Project Overview**: Objectives and architecture description.
- **Project Details**: Academic metadata, student information, and academic partner credentials.
- **Technology Stack**: Python, Streamlit, Pandas, Plotly.

---

## 3. Five Compulsory FA-2 Visualizations

| # | Visualization | Type | Key Fields |
|---|---|---|---|
| 1 | **Delay Analyzer** | Grouped Bar Chart | Weather, Traffic, Delivery_Time |
| 2 | **Vehicle Comparison** | Bar Chart | Vehicle, Delivery_Time |
| 3 | **Agent Performance** | Scatter Plot | Agent_Rating, Delivery_Time, Agent_Age_Group |
| 4 | **Area Heatmap** | 2D Heatmap | Area, Traffic, Delivery_Time |
| 5 | **Category Visualizer** | Boxplot | Category, Delivery_Time |

---

## 4. Data Preparation & Mathematical Modeling

### Late Delivery Definition
$$\text{Late\_Threshold} = \mu + s = \text{Mean}(\text{Delivery\_Time}) + \text{StdDev}(\text{Delivery\_Time}, \text{ddof}=1)$$

| Metric | Value |
|---|---:|
| **Total Records** | 43,739 |
| **Fleet Mean (μ)** | 124.9056 minutes |
| **Sample StdDev (s, ddof=1)** | 51.9155 minutes |
| **Late Threshold** | 176.8211 minutes |
| **Late Deliveries** | 7,171 (16.3950%) |
| **On-Time Deliveries** | 36,568 (83.6050%) |

### Data Cleaning — Field-Specific Handling
- **43,739 raw records** loaded; **0 duplicates** found; **0 rows dropped**.
- **91 records** with missing Weather/Traffic are excluded from weather/traffic charts only (not from KPIs).
- **54 records** with missing Agent_Rating are excluded from the scatter plot only.
- **53 records** with Agent_Rating = 6.0 are flagged but retained for transparency.
- **32,698 records** with "Metropolitian" spelling corrected to "Metropolitan".
- Vehicle names normalized to Title Case.

---

## 5. Global Filters

Five multiselect filters in the sidebar:
1. Weather Condition
2. Traffic Density
3. Vehicle Modality
4. Geographic Area
5. Product Category

- **Empty selection = All** (no filtering applied).
- **Apply Filters** commits selections and refreshes all KPIs, charts, and tables.
- **Reset Filters** restores the full dataset.
- Filter selections persist across section navigation via Streamlit session state.
- Late-delivery threshold remains constant regardless of filter selections.

---

## 6. Local Setup

```bash
# 1. Clone the repository
git clone <repository-url>
cd LogiSight-Analytics

# 2. Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
streamlit run app.py
```

The dashboard will open at `http://localhost:8501`.

---

## 7. Streamlit Cloud Deployment

1. Push the repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect the repository.
4. Set `app.py` as the main file.
5. Deploy.

Ensure `requirements.txt` and the `data/` folder with the CSV are included.

---

## 8. Project Structure

```text
LogiSight-Analytics/
├── app.py                              # Complete Streamlit application
├── requirements.txt                    # Python dependencies
├── README.md                           # This documentation
├── .gitignore                          # Git exclusions
├── .streamlit/
│   └── config.toml                     # Streamlit theme configuration
├── data/
│   └── Last_mile_Delivery_Data.csv     # Source dataset (43,739 records)
├── assets/
│   ├── wacp.png                        # WACP institutional logo
│   └── viraj.png                       # Viraj International logo
└── test_app.py                         # Automated test suite
```

---

## 9. Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core programming language |
| **Streamlit** | Web application framework |
| **Pandas** | Data loading, cleaning, and aggregation |
| **NumPy** | Numerical computations |
| **Plotly** | Interactive chart rendering |

---

*Developer: Ankit Pradhan (Roll: 1000390) | LogiSight Analytics Pvt. Ltd.*
*Powered by Python, Streamlit & Plotly | Deployed on Streamlit Cloud*
