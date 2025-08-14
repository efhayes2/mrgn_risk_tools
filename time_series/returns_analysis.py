import os
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# === Token label for plots ===
token_name = "hSOL"
freq = "15s"

# === Config ===
root = r'C:\data\crypto\prices\inputs'
# input_file = os.path.join(root, f"{token_name}_1m_ohlcv_backward_processed.csv")
input_file = os.path.join(root, f"{token_name}_{freq}_ohlcv_backward.csv")
pdf_file = os.path.join(root, f'{token_name}_{freq}_010125_072825.pdf')

# === Load data ===
df = pd.read_csv(input_file, parse_dates=["timestamp"])
df.set_index("timestamp", inplace=True)

# === Recompute returns if needed ===
df["return"] = df["close"].pct_change()
df = df[(df["return"] != 0) & (df["return"] <= 0.10) & (df["return"] >= -0.10)]

# === Inliers and Outliers ===
outliers = df[(df["return"] > 0.01) | (df["return"] < -0.01)]
inliers = df[df["return"].abs() < 0.01]

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
        output_rows.append(["", "", ""])
    return pd.DataFrame(output_rows, columns=["timestamp", "close", "return"])

top_returns = df["return"].nlargest(10)
bottom_returns = df["return"].nsmallest(10)

top_context = collect_and_format_context(df, top_returns)
bottom_context = collect_and_format_context(df, bottom_returns)

# === Combine top and bottom return context ===
def build_combined_return_context(top_context, bottom_context, n=10):
    rows = []
    for i in range(n):
        top_block = top_context.iloc[i * 4 : i * 4 + 3] if i * 4 + 2 < len(top_context) else pd.DataFrame([["", "", ""]] * 3, columns=top_context.columns)
        bottom_block = bottom_context.iloc[i * 4 : i * 4 + 3] if i * 4 + 2 < len(bottom_context) else pd.DataFrame([["", "", ""]] * 3, columns=bottom_context.columns)
        for j in range(3):
            rank_label = str(i + 1) if j == 1 else ""
            top_row = top_block.iloc[j].tolist()
            bottom_row = bottom_block.iloc[j].tolist()
            rows.append([rank_label] + top_row + bottom_row)
        rows.append(["", "", "", "", "", "", ""])
    combined_df = pd.DataFrame(rows, columns=[
        "Rank", "top_timestamp", "top_close", "top_return",
        "bottom_timestamp", "bottom_close", "bottom_return"
    ])
    combined_df["Rank"] = combined_df["Rank"].apply(lambda x: f"{x:>5}" if x else "")
    return combined_df

combined = build_combined_return_context(top_context, bottom_context, n=9)
combined.reset_index(drop=True, inplace=True)


def plot_histogram_with_stats(data, full_df, title, color):
    fig = plt.figure(figsize=(10, 6))
    data["return"].hist(bins=100, color=color, edgecolor="black")
    plt.title(f"{token_name} - {title}")
    plt.xlabel("Return")
    plt.ylabel("Frequency")

    # Add N_total and N_filtered box
    n_total = len(full_df)
    n_filtered = len(data)
    stats_text = f"N_total = {n_total:,}\nN_filtered = {n_filtered:,}"
    plt.gca().text(
        0.98, 0.98, stats_text,
        transform=plt.gca().transAxes,
        verticalalignment='top',
        horizontalalignment='right',
        fontsize=10,
        bbox=dict(facecolor='white', edgecolor='gray', boxstyle='round,pad=0.5')
    )

    plt.grid(True)
    plt.tight_layout()
    return fig


# === PDF Report ===
with PdfPages(pdf_file) as pdf:
    # Page 1: All Returns
    pdf.savefig(plot_histogram_with_stats(df, df, f"Histogram of {freq} Returns (All)", "steelblue"))
    plt.close()

    # Page 2: Outliers
    pdf.savefig(plot_histogram_with_stats(outliers, df, f"Histogram of {freq} Outlier Returns (>|1%|)", "crimson"))
    plt.close()

    # Page 3: Inliers
    pdf.savefig(plot_histogram_with_stats(inliers, df, f"Histogram of {freq} Inlier Returns (<|1%|)", "darkgreen"))
    plt.close()

    # Page 4: Combined Return Table in Landscape
    fig4, ax = plt.subplots(figsize=(14, 8))  # Landscape mode
    ax.axis('off')
    table = ax.table(
        cellText=combined.values,
        colLabels=combined.columns,
        loc='center',
        cellLoc='right',
        colLoc='right'
    )
    table.auto_set_font_size(False)
    table.set_fontsize(8)
    table.scale(1.2, 1.2)
    pdf.savefig(fig4)
    plt.close(fig4)

print(f"✅ PDF saved to: {pdf_file}")
