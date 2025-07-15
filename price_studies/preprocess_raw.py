from itertools import combinations
import numpy as np
import pandas as pd

save_dir = r'C:\Users\ehayes\OneDrive\a-mrgn\market_data'
input_file = "prices.xlsm"
output_file = "price_study.xlsx"

input_path = f"{save_dir}\\{input_file}"
output_path = f"{save_dir}\\{output_file}"

# Core settings
day_counts = [1, 3, 7]
full_cutoff = pd.Timestamp("2025-03-31 23:00:00")
filtered_start = pd.Timestamp("2024-01-01")
filtered_end = full_cutoff

# Load raw tabs
raw_sheets = {
    "sol_raw": pd.read_excel(input_path, sheet_name="sol_raw"),
    "jito_raw": pd.read_excel(input_path, sheet_name="jito_raw"),
    "msol_raw": pd.read_excel(input_path, sheet_name="msol_raw")
}

# Parse timestamps
for df in raw_sheets.values():
    df['timestamp'] = pd.to_datetime(df['timestamp'])

# Generic function for volatility & return
def add_features(df, num_hours, annualization_factor, window_sizes):
    df = df.sort_values("timestamp").set_index("timestamp")
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    for label, window in window_sizes.items():
        df[f'vol_{label}'] = df['log_return'].rolling(window).std() * annualization_factor**0.5
    return df.reset_index()

# Correlation
def add_rolling_corr(df, name1, name2, window_sizes):
    for label, window in window_sizes.items():
        df[f'corr_{label}'] = df[f'log_return_{name1}'].rolling(window).corr(df[f'log_return_{name2}'])
    return df

# Tail truncation
def truncate_trailing_windows(df, cutoff, window_sizes, vol_cols, corr_cols):
    df = df.copy()
    for label, window in window_sizes.items():
        tail_idx = df[df['timestamp'] <= cutoff].tail(window).index
        for col in vol_cols + corr_cols:
            if col in df.columns:
                df.loc[tail_idx, col] = np.nan
    return df

# Master generator
def create_pairwise_tabs(df_dict, resample_hours=1, tag_suffix="", date_filter=None):
    results = {}
    pairs = list(combinations(df_dict.items(), 2))
    num_hours = resample_hours
    samples_per_day = int(24 / num_hours)
    annualization_factor = 365 * 24 / num_hours
    window_sizes = {f'{d}d': d * samples_per_day for d in day_counts}

    for (name1, df1), (name2, df2) in pairs:
        base1 = df1.copy()
        base2 = df2.copy()

        if date_filter:
            base1 = base1[(base1['timestamp'] >= date_filter[0]) & (base1['timestamp'] <= date_filter[1])]
            base2 = base2[(base2['timestamp'] >= date_filter[0]) & (base2['timestamp'] <= date_filter[1])]

        min_ts = max(base1['timestamp'].min(), base2['timestamp'].min())
        base1 = base1[base1['timestamp'] >= min_ts]
        base2 = base2[base2['timestamp'] >= min_ts]

        # Resample and interpolate only numeric columns
        numeric_cols = ['close', 'volume']
        df1 = base1.set_index('timestamp')[numeric_cols].resample(f'{num_hours}h').mean().interpolate().reset_index()
        df2 = base2.set_index('timestamp')[numeric_cols].resample(f'{num_hours}h').mean().interpolate().reset_index()

        # Filter for even hours if num_hours == 2
        if num_hours == 2:
            df1 = df1[df1['timestamp'].dt.hour % 2 == 0]
            df2 = df2[df2['timestamp'].dt.hour % 2 == 0]

        df1['symbol'] = name1.replace('_raw', '').upper()
        df1['hr'] = df1['timestamp'].dt.hour
        df2['symbol'] = name2.replace('_raw', '').upper()
        df2['hr'] = df2['timestamp'].dt.hour

        df1_feat = add_features(df1[['timestamp', 'hr', 'symbol', 'close', 'volume']], num_hours, annualization_factor, window_sizes)
        df2_feat = add_features(df2[['timestamp', 'hr', 'symbol', 'close', 'volume']], num_hours, annualization_factor, window_sizes)

        # Rename
        key1 = name1.replace('_raw', '')
        key2 = name2.replace('_raw', '')

        df1_feat = df1_feat.rename(columns={
            'hr': f'hr_{key1}',
            'symbol': f'symbol_{key1}',
            'close': f'close_{key1}',
            'log_return': f'log_return_{key1}',
            **{f'vol_{label}': f'vol_{label}_{key1}' for label in window_sizes}
        })
        df2_feat = df2_feat.rename(columns={
            'hr': f'hr_{key2}',
            'symbol': f'symbol_{key2}',
            'close': f'close_{key2}',
            'log_return': f'log_return_{key2}',
            **{f'vol_{label}': f'vol_{label}_{key2}' for label in window_sizes}
        })

        merged = pd.merge(df1_feat, df2_feat, on='timestamp')
        merged = merged[merged['timestamp'] <= full_cutoff]

        # Rolling corr
        merged = add_rolling_corr(merged, key1, key2, window_sizes)

        vol_cols = [f'vol_{label}_{key1}' for label in window_sizes] + [f'vol_{label}_{key2}' for label in window_sizes]
        corr_cols = [f'corr_{label}' for label in window_sizes]

        # merged = truncate_trailing_windows(merged, full_cutoff, window_sizes, vol_cols, corr_cols)

        ordered = ['timestamp',
            f'hr_{key1}', f'symbol_{key1}', f'close_{key1}', f'log_return_{key1}',
            *[f'vol_{label}_{key1}' for label in window_sizes],
            f'hr_{key2}', f'symbol_{key2}', f'close_{key2}', f'log_return_{key2}',
            *[f'vol_{label}_{key2}' for label in window_sizes],
            *corr_cols
        ]

        results[f"{key1}_{key2}{tag_suffix}"] = merged[ordered]

    return results

# Generate all 9 pairwise tabs
full_tabs = create_pairwise_tabs(raw_sheets, resample_hours=1)
day_tabs = create_pairwise_tabs(raw_sheets, resample_hours=1, tag_suffix="_filtered", date_filter=(filtered_start, filtered_end))
hour_tabs = create_pairwise_tabs(raw_sheets, resample_hours=2, tag_suffix="_hours_filtered", date_filter=(filtered_start, filtered_end))

# Write all 12 tabs
with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
    # 3 raw
    # for name, df in raw_sheets.items():
    #     df.to_excel(writer, sheet_name=name, index=False)
    # # 3 full
    # for name, df in full_tabs.items():
    #     df.to_excel(writer, sheet_name=name, index=False)
    # 3 filtered (days)
    for name, df in day_tabs.items():
        df.to_excel(writer, sheet_name=name, index=False)
    # 3 filtered (even hours)
    for name, df in hour_tabs.items():
        df.to_excel(writer, sheet_name=name, index=False)

print(f"Workbook saved to: {output_path}")
