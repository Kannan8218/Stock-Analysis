# 📊 Data-Driven Stock Analysis: Organizing, Cleaning, and Visualizing Market Trends

## 📁 Project Overview

This project aims to create an interactive **Stock Performance Dashboard** by analyzing the **Nifty 50** stocks over the past year. It extracts, organizes, cleans, and analyzes stock market data provided in **YAML** format and presents insightful visualizations using **Power BI** and **Streamlit**.

### 📦 Data Source

- All raw data files are located in the `data/` folder, which is included as a ZIP archive in the project.
- The stock data is organized in **YAML format**, structured by month and date, inside the ZIP file.

### 🔍 Problem Statement

- Extract and clean daily stock data (open, high, low, close, volume).
- Identify the **top and worst-performing stocks**.
- Analyze **market volatility**, **cumulative returns**, **sector-wise performance**, and **price correlations**.
- Provide **monthly top gainers and losers**.
- Create **interactive dashboards** to support **data-driven investment decisions**.

## 🧰 Skills You Will Learn

- 🐍 Python, Pandas, Yaml, Glob, Os
- 📊 Power BI, Streamlit, seaborn
- 🧮 Statistics, Data Analysis
- 🗂️ Data Organizing, Cleaning, and Transformation
- 📈 Financial Analytics

## 📂 Domain

- Finance
- Data Analytics

## 🧠 Business Use Cases

1. **Stock Performance Ranking:**  
   Discover the top 10 gainers (green stocks) and top 10 losers (red stocks).

2. **Market Overview:**  
   See the overall market summary and the distribution of green vs. red stocks.

3. **Investment Insights:**  
   Identify stocks showing consistent growth or significant declines.

4. **Decision Support:**  
   Analyze average prices, trading volumes, volatility, and stock behavior.

## ⚙️ Project Structure

📁 data/ └── YAML files organized by month and date  
📁 output/ └── 50 CSV files (one for each stock symbol)  
📄 stock_analysis.py  
📄 sector_mapping.csv

## 🧪 Approach

### 1. Data Extraction and Transformation

- Parse YAML files containing stock data for each month.
- Organize data by stock symbol and store it as 50 individual CSV files.

### 2. Data Cleaning & Analysis

- Standardize missing values and format columns.
- Calculate:
  - Daily returns
  - Yearly cumulative return
  - Standard deviation (volatility)
  - Monthly percentage return
  - Correlation matrix

## 📊 Visualization Modules

### ✅ Top 10 Gainers & Losers
- Sort by yearly return.
- Show green and red stocks using horizontal bar charts.

### 📌 Market Summary
- Number of green vs. red stocks.
- Average price and volume across the market.

### 📈 Volatility Analysis
- Standard deviation of daily returns.
- Bar chart of the top 10 most volatile stocks.

### 🔁 Cumulative Return
- Running total of daily returns.
- Line chart for top 5 performing stocks.

### 🏭 Sector-wise Performance
- Join with sector mapping CSV.
- Bar chart of average yearly return by sector.

### 🔄 Stock Price Correlation
- Generate correlation matrix using `.corr()`.
- Visualized with a heatmap.

### 📆 Top Gainers & Losers (Month-wise)
- Monthly breakdown of top 5 gainers and losers.
- 12 charts, one for each month.

## 🚀 How to Run

### 🔧 Requirements

Install dependencies:


pip install pandas pyyaml matplotlib seaborn streamlit
▶️ Run the Python Script

python stock_analysis.py
🌐 Run Streamlit Dashboard

streamlit run stock_analysis.py
📊 Open Power BI Dashboard
Use the Power BI .pbix file provided (if available) to view the advanced dashboard insights.

📜 Sample Visuals
Visuals are generated using Streamlit and Matplotlib/Seaborn. You can integrate additional charts into Power BI for enhanced BI capabilities.

📂 Folder Outputs
After running the script:

✅ output/ folder contains CSVs for each stock.
✅ Summary statistics and visual charts saved.
✅ Visuals displayed in Streamlit UI.

📃 License
Permission is hereby granted, free of charge...

✍️ Author
Kannan D

🤝 Contributing
Contributions, issues, and feature requests are welcome!
