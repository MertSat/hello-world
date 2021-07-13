pip install yfinance
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
pd.options.mode.chained_assignment = None

tickers = pd.read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")[0]. #ticker şirket kısaltması

tickers = tickers.Symbol.to_list()

tickers = [i.replace(".","-") for i in tickers]

tickers.pop(491) #sıkıntı olan 2 tane ticker varmış sadece 1 i benim listemdeydi onu attım

def RSIcalc(asset):
    df = yf.download(asset, start = "2011-01-01") 
    df["MA200"] = df["Adj Close"].rolling(window = 200).mean()
    df["Price_Change"] = df["Adj Close"].pct_change()
    df["Up_Move"] = df["Price_Change"].apply(lambda x: x if x > 0 else 0)
    df["Down_Move"] = df["Price_Change"].apply(lambda x: abs(x) if x < 0 else 0)
    df["Avg_Up"] = df["Up_Move"].ewm(span = 19).mean()
    df["Avg_Down"] = df["Down_Move"].ewm(span = 19).mean()      
    df = df.dropna()
    df["RS"] = df["Avg_Up"]/df["Avg_Down"]
    df["RSI"] = df["RS"].apply(lambda x: 100 - (100/(x+1))) 
    df.loc[(df["Adj Close"] > df["MA200"]) & (df["RSI"] < 30), "Buy"] = "Yes"  
    df.loc[(df["Adj Close"] < df["MA200"]) | (df["RSI"] > 30), "Buy"] = "No"  
    return df 
    
def getSignals(df):
    Buying_dates = []
    Selling_dates = []
    
    for i in range(len(df) - 11):
        if "Yes" in df["Buy"].iloc[i]:
            Buying_dates.append(df.iloc[i+1].name)
            for j in range(1,11):
                if df["RSI"].iloc[i + j] > 40:
                    Selling_dates.append(df.iloc[i+j+1].name)
                    break
                elif j== 10:
                    Selling_dates.append(df.iloc[i+j+1].name)
        
    return Buying_dates, Selling_dates
    
frame = RSIcalc(tickers[0])
buy, sell = getSignals(frame)

plt.figure(figsize=(12,5))
plt.scatter(frame.loc[buy].index, frame.loc[buy]["Adj Close"], marker="^", c="g")
plt.plot(frame["Adj Close"], alpha = 0.7)

Profits = (frame.loc[sell].Open.values - frame.loc[buy].Open.values)/frame.loc[buy].Open.values


matrixsignals = []
matrixprofits = []

for i in range(len(tickers)):
    frame = RSIcalc(tickers[i])
    buy,sell = getSignals(frame)
    Profits = (frame.loc[sell].Open.values - frame.loc[buy].Open.values)/frame.loc[buy].Open.values
    matrixsignals.append(buy)
    matrixprofits.append(Profits)

    
