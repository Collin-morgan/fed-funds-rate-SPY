
import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import datetime as dt
import matplotlib.pyplot as plt

# === CONFIGURATION ===
start = dt.datetime(2010, 1, 1)
end = dt.datetime(2024, 6, 1)

# === DOWNLOAD SPY DATA ===
spy = yf.download("SPY", start=start, end=end)
spy = spy["Adj Close"].resample("M").last()

# === DOWNLOAD FED FUNDS RATE DATA ===
fed_funds = web.DataReader("FEDFUNDS", "fred", start, end)
fed_funds = fed_funds.resample("M").last()

# === MERGE DATA ===
df = pd.concat([spy, fed_funds], axis=1)
df.columns = ["SPY", "FedFunds"]
df.dropna(inplace=True)

# === STRATEGY ===
# Signal: Buy if Fed Funds Rate has decreased compared to last month
df["Signal"] = df["FedFunds"].diff() < 0
df["Position"] = df["Signal"].shift(1).fillna(False)

# Calculate returns
df["SPY_Return"] = df["SPY"].pct_change()
df["Strategy_Return"] = df["SPY_Return"] * df["Position"]

# Compute equity curves
df["BuyHold_Equity"] = (1 + df["SPY_Return"]).cumprod()
df["Strategy_Equity"] = (1 + df["Strategy_Return"]).cumprod()

# === METRICS ===
total_return = df["Strategy_Equity"].iloc[-1] - 1
sharpe_ratio = (df["Strategy_Return"].mean() / df["Strategy_Return"].std()) * (12**0.5)
max_drawdown = (df["Strategy_Equity"].cummax() - df["Strategy_Equity"]).max()

print(f"Total Return: {total_return:.2%}")
print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
print(f"Max Drawdown: {max_drawdown:.2%}")

# === PLOT ===
plt.figure(figsize=(10, 6))
plt.plot(df.index, df["Strategy_Equity"], label="Fed Funds Strategy")
plt.plot(df.index, df["BuyHold_Equity"], label="Buy & Hold SPY")
plt.title("Fed Funds Rate Strategy vs Buy & Hold SPY")
plt.xlabel("Date")
plt.ylabel("Growth of $1")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("fed_funds_strategy_chart.png")
plt.show()

# === SAVE DATA ===
df.to_csv("fed_funds_strategy_data.csv")
