import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt

# === Config ===
root = r'C:\data\crypto\crypto_archive\inputs'
file_name = "mSOL_1m_ohlcv_backward.csv"
input_file = os.path.join(root, file_name)

file_name = "mSOL_1m_ohlcv_backward_processed.csv"
output_file = os.path.join(root, file_name)

histogram_file = output_file.replace(".csv", "_returns_histogram.png")
outliers_file = output_file.replace(".csv", "_returns_histogram_outliers.png")

# === Load CSV with timestamp parsing ===
df = pd.read_csv(input_file, parse_dates=["timestamp"])
df.set_index("timestamp", inplace=True)

# === Drop rows before Selected Date ===
cutoff = datetime.datetime(2024, 7, 1, tzinfo=datetime.UTC)
df = df[df.index >= cutoff]

# === Compute minute return ===
df["return"] = df["close"].pct_change()

# === Filter out 0 and extreme returns (>10% or <-10%) ===
df = df[(df["return"] != 0) & (df["return"] <= 0.10) & (df["return"] >= -0.10)]

# === Add formatted return column ===
df["formatted_return"] = (df["return"] * 100).map("{:+.2f}%".format)

# === Save cleaned data ===
os.makedirs(os.path.dirname(output_file), exist_ok=True)
df.to_csv(output_file)

# === Histogram: Full Returns ===
plt.figure(figsize=(10, 6))
df["return"].hist(bins=100, color='steelblue', edgecolor='black')
plt.title("Histogram of 1-Minute Returns (Filtered)")
plt.xlabel("Return")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig(histogram_file)
plt.show()

# === Histogram: Outliers >1% or <-1% (still within ±10%) ===
outliers = df[(df["return"] > 0.01) | (df["return"] < -0.01)]

plt.figure(figsize=(10, 6))
outliers["return"].hist(bins=100, color='crimson', edgecolor='black')
plt.title("Histogram of Outlier Returns (>|1%| and <|10%|)")
plt.xlabel("Return")
plt.ylabel("Frequency")
plt.grid(True)
plt.tight_layout()
plt.savefig(outliers_file)
plt.show()


# === Collect 3-row Context and Format Output ===
def collect_and_format_context(df, returns):
    output_rows = []
    for idx in returns.index:
        loc = df.index.get_loc(idx)
        start = max(loc - 1, 0)
        end = min(loc + 1, len(df) - 1)
        for i in range(start, end + 1):
            ts = df.index[i].strftime("%Y-%m-%d %H:%M:%S")
            close = f"{df.iloc[i]['close']:8.3f}"
            ret = df.iloc[i]["return"]
            formatted = f"{'+' if ret >= 0 else '-'}{abs(ret) * 100:6.2f}%"
            output_rows.append([ts, close, formatted])

        # Append a blank row
        output_rows.append(["", "", ""])

    return pd.DataFrame(output_rows, columns=["timestamp", "close", "return"])


# === Generate and Display Results ===
top_output = collect_and_format_context(df, df["return"].nlargest(10))
bottom_output = collect_and_format_context(df, df["return"].nsmallest(10))

print("\n📈 Top 10 1-Minute Returns (with context):")
print(top_output.to_string(index=False))

print("\n📉 Bottom 10 1-Minute Returns (with context):")
print(bottom_output.to_string(index=False))
temp = 1