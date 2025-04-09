from datetime import datetime, timedelta 
import glob
import yaml
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os 
from pathlib import Path
import mysql.connector
from mysql.connector import Error
import streamlit as st 
class stock:
    def __init__(self):
        self.dateRange = None
        self.rawData = None
        self.sectorData = None
        self.stockData = None
        self.volatility_df = None
        self.cumulative_df = None
        self.sectorWise_df = None
        self.stockPrice_df = None
        self.TopGainersLosers_df = None
        self.top5_cum = None
        self.conn = None
        self.mycursor = None
        print("✅ class object created successfully ") 
    def database(self):
        try:
            self.conn = mysql.connector.connect(host='localhost', user='root', password='')
            if self.conn.is_connected():
                print("Connected to MySQL Server")
                self.mycursor = self.conn.cursor()
                self.mycursor.execute("CREATE DATABASE IF NOT EXISTS StockAnalysis")
        except Error as e:
            print("❌ Error while connecting to MySQL:", e)
            return False
        return True 
    def date_range(self):
        def fun():
            sd = datetime(2023, 10, 1) #set start date
            ed = datetime(2024, 11, 22) #set end date
            r = []
            while sd <= ed:
                r.append(sd.strftime("%Y-%m"))  #format like YYYY-MM
                nm = sd.month + 1 if sd.month < 12 else 1 #for next month
                ny = sd.year if sd.month < 12 else sd.year + 1 #for next year
                sd = datetime(ny, nm, 1)
            return r
        a = fun()
        return a
    def data_exctract(self):
        t1, t2 = 0, 0 
        self.dateRange = self.date_range()
        if (self.dateRange == None) or (len(self.dateRange) == 0):
            print("something wrong in generate date range")
            return False
        print("month-year list:", self.dateRange)
        df = []
        for sub_folder_path in self.dateRange: #here 'self.dateRange' variable contain month-year values(fun())
            try:
                yaml_files = glob.glob(f"data/{sub_folder_path}/*.yaml") #get all .yaml files in current subfolder
            except Exception as e:
                pass
                #print(f"error -> data_exctract folder -> for loop(read all YAML files)\nERROR : {e}")
                #return False
            for file in yaml_files: #for read all .yaml files
                with open(file, "r") as f:
                    try:
                        yaml_data = yaml.safe_load(f)
                    except Exception as e:
                        print(f"error -> data_exctract folder -> for loop(safe load YAML files)\nERROR : {e}")
                        return False
                    if yaml_data:
                        t1 += 1
                        d = pd.DataFrame(yaml_data)
                        df.append(d)
                    else:
                        t2 = t2 + 1
        print(f"total no of readed YAML files count -> {t1}")
        print(f"total no of unreaded YAML files count -> {t2}")
        if df: 
            self.rawData = pd.concat(df, ignore_index=True) #concatenate all DataFrames into single Dataframe
            print(f"total {self.rawData.shape[0]} rows in over all files" )
        else:
            print("something wrong check inside data folder or sub-folders")
            return False
        return True
    def data_clean(self):
        try:
            self.sectorData = pd.read_csv("Sector_data - Sheet1.csv")
        except Exception as e:
            print(f"Error -> data_clean function(read 'Sector_data - Sheet1.csv')\nError : {e}")
            print("Check 'Sector_data - Sheet1.csv' file available or not")
            return False
        print(f"no of NaN values: {self.rawData.isna().sum().sum()}")
        print(f"no of 0 values: {(self.rawData == 0).sum().sum()}")
        print("count of unique values in 'Ticker' column: ",len(self.rawData['Ticker'].unique())) #check unique values in 'Ticker' column
        self.rawData.to_csv("raw_data.csv", index = False)
        try:
            os.makedirs("separated_files/", exist_ok=True) #create separated_files folder
        except Exception as e:
            print(f"Error -> data_clean function(can't make 'separated_files/' directory)\nError : {e}")
            return False
        for ticker, group in self.rawData.groupby("Ticker"):
            try:
                file_name = os.path.join("separated_files/", f"{ticker}.csv")  # Use os.path.join for cross-platform support
                group.to_csv(file_name, index=False)
            except Exception as e:
                print(f"Error -> data_clean function -> for loop(can't create 'Ticker based .csv files in 'separated_files/' directory)\nError : {e}")
                return False
        saved_files = glob.glob(os.path.join("separated_files/", "*.csv"))
        print(f"Data separated and saved as {len(saved_files)} individual CSV files!")
        try:
            csv_files = glob.glob("separated_files/*.csv") #load all csv files in separated_files folder into dictionary
        except Exception as e:
            print(f"Error -> data_clean function(can't read all .csv files in 'separated_files/' directory)\nError : {e}")
            return False
        self.stockData = {}
        for file in csv_files:
            ticker = os.path.basename(file).replace(".csv", "")
            self.stockData[ticker] = pd.read_csv(file)
        return True
    def Volatility(self):
        volatility_results = []
        if self.stockData:
            for ticker, df in self.stockData.items():
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df['DailyReturn'] = df['close'].pct_change()
                volatility = df['DailyReturn'].std()
                volatility_results.append({'Ticker': ticker, 'Volatility': volatility})
            volatility_df = pd.DataFrame(volatility_results)
            volatility_df = volatility_df.sort_values(by='Volatility', ascending=False)
            volatility_df.to_csv("volatility.csv", index = False)
        else:
            print("problem -> Volatility(self.stockData dictionary is Empty)")
            return False
        data = pd.read_csv("volatility.csv")
        self.mycursor.execute("USE StockAnalysis")
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS volatility (Ticker VARCHAR(225) PRIMARY KEY,Volatility FLOAT)""")
        for _, row in data.iterrows():
            try:
                self.mycursor.execute("""INSERT INTO volatility (Ticker, Volatility) VALUES (%s, %s)""", (row['Ticker'], row['Volatility']))
            except mysql.connector.IntegrityError:
                pass
        self.conn.commit()
        print("✅ Volatility Data inserted into MySQL 'volatility' table.")
        return True
    def Cumulative(self):
        cum_returns = {}
        if self.stockData:
            for ticker, df in self.stockData.items():
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df['DailyReturn'] = df['close'].pct_change()
                df['CumulativeReturn'] = (1 + df['DailyReturn']).cumprod()
                cum_returns[ticker] = df.set_index('date')['CumulativeReturn']
            cum_returns_df = pd.concat(cum_returns, axis=1)
            final_returns = cum_returns_df.ffill().iloc[-1].sort_values(ascending=False)
            self.top5_cum = final_returns.head(5).index
            cum_returns_df.to_csv("cumulative.csv")
        else:
            print("problem -> Cumulative(self.stockData dictionary is Empty)")
            return False
        df = pd.read_csv("cumulative.csv", parse_dates=["date"])
        df['date'] = df['date'].dt.date
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS cumulative_returns (
            Ticker VARCHAR(225), Date DATE, CumulativeReturn FLOAT, PRIMARY KEY (Ticker, Date))""")
        for _, row in df.iterrows():
            for ticker in df.columns[1:]:
                try:
                    self.mycursor.execute("""INSERT INTO cumulative_returns (Ticker, Date, CumulativeReturn)
                        VALUES (%s, %s, %s)""", (ticker, row['date'], row[ticker]))
                except Exception:
                    pass  
        self.conn.commit()
        print("✅ cumulative return Data inserted into 'volatility' table.")
        return True
    def Sector_wise(self):
        if self.stockData:
            if 'Symbol' in self.sectorData.columns:
                self.sectorData['Ticker'] = self.sectorData['Symbol'].apply(
                    lambda x: x.split(':')[1].strip().upper() if ':' in x else x.strip().upper())
            else:
                print("Column 'Symbol' not found in Sector_data.")
            self.rawData['Ticker'] = self.rawData['Ticker'].str.strip().str.upper()
            print("Checking for unmatched tickers between both files...")
            tickers_raw = set(self.rawData['Ticker'].dropna().unique())
            tickers_sector = set(self.sectorData['Ticker'].dropna().unique())
            common_tickers = tickers_raw.intersection(tickers_sector)
            only_in_raw = tickers_raw - tickers_sector
            only_in_sector = tickers_sector - tickers_raw
            if (len(only_in_raw) > 0) or (len(only_in_sector) > 0):
                print(f"{len(common_tickers)} common 'Ticker' values in both files")
                print(f"{len(only_in_raw)} tickers only in over all dataset: {only_in_raw}")
                print(f"{len(only_in_sector)} tickers only in Sector_data-Sheet1.csv: {only_in_sector}")
            else:
                print("All values in both files match!")
            self.rawData = self.rawData[self.rawData['Ticker'].isin(common_tickers)]
            self.sectorData = self.sectorData[self.sectorData['Ticker'].isin(common_tickers)]
            copy_raw_data = self.rawData.copy()
            copy_sector_data = self.sectorData.copy()
            copy_raw_data['date'] = pd.to_datetime(copy_raw_data['date'])
            copy_raw_data = copy_raw_data.sort_values(by=['Ticker', 'date'])
            copy_raw_data['year'] = copy_raw_data['date'].dt.year
            returns = copy_raw_data.groupby(['Ticker', 'year'])['close'].agg(['first', 'last']).reset_index()
            returns['yearly_return'] = (returns['last'] - returns['first']) / returns['first']
            avg_returns = returns.groupby('Ticker')['yearly_return'].mean().reset_index()
            sector_info = copy_sector_data[['Ticker', 'sector']]
            merged = pd.merge(avg_returns, sector_info, on='Ticker')
            print("merged shape : ",merged.shape)
            sector_performance = merged.groupby('sector')['yearly_return'].mean().sort_values(ascending=False)
            sector_performance.to_csv("sector_wise.csv")
        else:
            print("problem -> Sector_wise(self.stockData dictionary is Empty)")
            return False
        sector_performance = pd.read_csv("sector_wise.csv")
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS sector_performance (
        sector VARCHAR(100) PRIMARY KEY, yearly_return FLOAT)""")
        for _, row in sector_performance.iterrows():
            try:
                self.mycursor.execute("""INSERT INTO sector_performance (sector, yearly_return) VALUES (%s, %s)
                    ON DUPLICATE KEY UPDATE yearly_return = VALUES(yearly_return)""", (row['sector'], row['yearly_return']))
            except Exception as e:
                print("Error inserting row:", e)
        self.conn.commit()
        print("✅ Sector-wise Performance Data inserted into 'sector_performance' table.")
        return True
    def Stock_price(self):
        close_prices = []
        tickers = []
        if self.stockData:
            for ticker, df in self.stockData.items():
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df = df.set_index('date')
                close_prices.append(df['close'])
                tickers.append(ticker)
            close_df = pd.concat(close_prices, axis=1)
            close_df.columns = tickers
            close_df.to_csv("stock_price.csv")
        else:
            print("problem -> Stock_price(self.stockData dictionary is Empty)")
            return False
        df = pd.read_csv("stock_price.csv", parse_dates=["date"])
        df.set_index("date", inplace=True)
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS stock_prices (Ticker VARCHAR(20), Date DATE, Close FLOAT, PRIMARY KEY (Ticker, Date))""")
        for ticker in df.columns:
            for date, value in df[ticker].dropna().items():
                try:
                    self.mycursor.execute("""
                        INSERT INTO stock_prices (Ticker, Date, Close)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE Close = VALUES(Close)
                    """, (ticker, date.strftime('%Y-%m-%d'), value))
                except Exception as e:
                    print(f"Error inserting {ticker} on {date}: {e}")
        self.conn.commit()
        print("✅ stock_prices table updated with close prices.")
        returns = df.pct_change()
        correlation_matrix = returns.corr()
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS stock_correlation (Ticker1 VARCHAR(20),Ticker2 VARCHAR(20), Correlation FLOAT, PRIMARY KEY (Ticker1, Ticker2))""")
        for t1 in correlation_matrix.columns:
            for t2 in correlation_matrix.index:
                corr_val = correlation_matrix.loc[t1, t2]
                try:
                    self.mycursor.execute("""INSERT INTO stock_correlation (Ticker1, Ticker2, Correlation)
                        VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE Correlation = VALUES(Correlation)""", (t1, t2, corr_val))
                except Exception as e:
                    print(f"Error inserting correlation for {t1}-{t2}: {e}")
        self.conn.commit()
        print("✅ Correlation matrix stored in MySQL.")
        return True
    def Top_Gain_Loss(self):
        monthly_rankings = []
        if self.stockData:
            for ticker, df in self.stockData.items():
                df['date'] = pd.to_datetime(df['date'])
                df = df.sort_values('date')
                df['Month'] = df['date'].dt.to_period('M')
                df['MonthlyReturn'] = df['close'].pct_change()
                monthly_return = df.groupby('Month')['close'].apply(lambda x: (x.iloc[-1] - x.iloc[0]) / x.iloc[0])
                temp_df = pd.DataFrame({'Month': monthly_return.index.astype(str), 'Ticker': ticker, 'MonthlyReturn': monthly_return.values})
                monthly_rankings.append(temp_df)
            monthly_returns = pd.concat(monthly_rankings)
            monthly_returns.to_csv("Top5_Gainers_Losers.csv",index = False)
        else:
            print("problem -> Volatility(self.stockData dictionary is Empty)")
            return False
        df = pd.read_csv("Top5_Gainers_Losers.csv")
        self.mycursor.execute("""CREATE TABLE IF NOT EXISTS monthly_gainers_losers (
                Month VARCHAR(20),Ticker VARCHAR(20),MonthlyReturn FLOAT)""")
        for _, row in df.iterrows():
            self.mycursor.execute("""INSERT INTO monthly_gainers_losers (Month, Ticker, MonthlyReturn)
                VALUES (%s, %s, %s)""", (row['Month'], row['Ticker'], row['MonthlyReturn']))
        self.conn.commit()
        return True
    def streamlit_visual(self):
        st.title("📊 Stock Analysis Dashboard")
        analysis_type = st.sidebar.radio("Select Analysis Type",
    ["Volatility Analysis","Cumulative return", "Sector-wise performances","Stock Price Correlation", "Top 5 Gainers and Losers" ])
        if analysis_type == "Volatility Analysis":
            self.mycursor.execute("SELECT Ticker, Volatility FROM volatility ORDER BY Volatility DESC LIMIT 10")
            rows = self.mycursor.fetchall()
            top_df = pd.DataFrame(rows, columns=['Ticker', 'Volatility'])
            st.subheader("Top 10 most volatile stocks over the year")
            st.dataframe(top_df, use_container_width=True)
            st.bar_chart(top_df.set_index('Ticker'))
        elif analysis_type == "Cumulative return":
            self.mycursor.execute("SELECT MAX(Date) FROM cumulative_returns")
            latest_date = self.mycursor.fetchone()[0]
            self.mycursor.execute("""SELECT Ticker, CumulativeReturn FROM cumulative_returns
                WHERE Date = %s ORDER BY CumulativeReturn DESC LIMIT 5""", (latest_date,))
            top5 = self.mycursor.fetchall()
            top5_tickers = [row[0] for row in top5]
            format_strings = ','.join(['%s'] * len(top5_tickers))
            self.mycursor.execute(f"""SELECT Ticker, Date, CumulativeReturn FROM cumulative_returns
                WHERE Ticker IN ({format_strings}) ORDER BY Date""", tuple(top5_tickers))
            rows = self.mycursor.fetchall()
            plot_df = pd.DataFrame(rows, columns=['Ticker', 'Date', 'CumulativeReturn'])
            plot_df['Date'] = pd.to_datetime(plot_df['Date'])
            pivot_df = plot_df.pivot(index='Date', columns='Ticker', values='CumulativeReturn')
            st.subheader("Top 5 Performing Stocks")
            st.line_chart(pivot_df.ffill())
        elif analysis_type == "Sector-wise performances":
            self.mycursor.execute("""SELECT sector, yearly_return FROM sector_performance ORDER BY yearly_return DESC""")
            data = self.mycursor.fetchall()
            sector_df = pd.DataFrame(data, columns=['Sector', 'AvgYearlyReturn'])
            st.subheader("The average performance for each sector")
            chart_df = sector_df.set_index('Sector')[['AvgYearlyReturn']]
            st.bar_chart(chart_df)
        elif analysis_type == "Stock Price Correlation" :
            self.mycursor.execute("SELECT Ticker1, Ticker2, Correlation FROM stock_correlation")
            rows = self.mycursor.fetchall()
            corr_df = pd.DataFrame(rows, columns=["Ticker1", "Ticker2", "Correlation"])
            pivot_corr = corr_df.pivot(index="Ticker1", columns="Ticker2", values="Correlation")
            if not pivot_corr.empty:
                st.subheader("Stock Price Correlation Heatmap")
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(pivot_corr, annot=False, cmap="coolwarm", linewidths=0.5, ax=ax)
                ax.set_title("Correlation matrix to visualize these relationships")
                plt.tight_layout()
                st.pyplot(fig)
        elif analysis_type == "Top 5 Gainers and Losers" :
            st.subheader("Monthly Top 5 Gainers & Losers (in%)")
            @st.cache_data
            def load_data():
                df = pd.read_csv("Top5_Gainers_Losers.csv")
                return df
            df = load_data()
            required_cols = {"Month", "Ticker", "MonthlyReturn"}
            if not required_cols.issubset(df.columns):
                st.error("The CSV is missing required columns. Expected columns: Month, Ticker, MonthlyReturn")
                st.stop()
            df['MonthlyReturn'] = df['MonthlyReturn'] * 100
            months = sorted(df['Month'].unique())
            # Loop through each month and plot Top 5 Gainers & Losers
            for month in months:
                month_df = df[df['Month'] == month]
                top5 = month_df.sort_values(by='MonthlyReturn', ascending=False).head(5)
                bottom5 = month_df.sort_values(by='MonthlyReturn', ascending=True).head(5)
                fig, axs = plt.subplots(1, 2, figsize=(14, 5))
                axs[0].bar(top5['Ticker'], top5['MonthlyReturn'], color='mediumseagreen', edgecolor='black')
                axs[0].set_title(f"Top 5 Gainers - {month}")
                axs[0].set_ylabel("Monthly Return (%)")
                axs[0].set_xlabel("Ticker")
                axs[1].bar(bottom5['Ticker'], bottom5['MonthlyReturn'], color='indianred', edgecolor='black')
                axs[1].set_title(f"Top 5 Losers - {month}")
                axs[1].set_ylabel("Monthly Return (%)")
                axs[1].set_xlabel("Ticker")
                plt.suptitle(f"📈 Monthly Gainers & Losers - {month}", fontsize=16, fontweight='bold')
                plt.tight_layout()
                with st.expander(f"📋 Show Data for {month}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Top 5 Gainers (%)**")
                        st.dataframe(top5)
                    with col2:
                        st.markdown("**Top 5 Losers (%)**")
                        st.dataframe(bottom5)
                st.pyplot(fig)
        else:
            st.info(f"🛠️ '{analysis_type}' not implemented yet.")     
if __name__ == "__main__":
    obj = stock()
    if obj.database():
        print("✅ successfully 'StockAnalysis' Database created.")
        if obj.data_exctract():
            print("✅ Successfully convert YAML Files into .csv files")
            if obj.data_clean():
                print("✅ Successfully data cleaned and creates .csv files in 'separated_files/'")
                if obj.Volatility():
                    print("✅ Successfully created Volatility Analysis dataframe and 'volatility.csv' file")
                    if obj.Cumulative():
                        print("✅ Successfully created Cumulative Return Over Time dataframe and 'cumulative.csv' file")
                        if obj.Sector_wise():
                            print("✅ Successfully created Sector-wise Performance dataframe and 'sector_wise.csv' file")
                            if obj.Stock_price():
                                print("✅ Successfully created  Stock Price Correlation dataframe and 'stock_price.csv' file")
                                if obj.Top_Gain_Loss():
                                    print("✅ Successfully created  Top 5 Gainers and Losers by Month dataframe and 'Top5_Gainers_Losers.csv' file")
                                    if obj.streamlit_visual():
                                        obj.conn.close()
                                        obj.mycursor.close()
                                        print("done")

