import pandas as pd
import numpy as np
from itertools import combinations
import os

class PriceStudyProcessor:
    def __init__(self, day_counts, filtered_start, filtered_end, tokens, output_name,
                 write_raw=False, write_full=False, write_filtered_days=True,
                 write_filtered_hours=True):
        self.day_counts = day_counts
        self.filtered_start = filtered_start
        self.filtered_end = filtered_end
        self.tokens = tokens
        self.output_name = output_name
        self.write_raw = write_raw
        self.write_full = write_full
        self.write_filtered_days = write_filtered_days
        self.write_filtered_hours = write_filtered_hours

        self.raw_sheets = {}
        self.tab_groups = {}

    def load_data(self, input_path):
        for token in self.tokens:
            sheet_name = f"{token}_raw"
            self.raw_sheets[sheet_name] = pd.read_excel(input_path, sheet_name=sheet_name)
            self.raw_sheets[sheet_name]['timestamp'] = pd.to_datetime(self.raw_sheets[sheet_name]['timestamp'])

    def add_features(self, df, num_hours, annualization_factor, window_sizes):
        df = df.sort_values("timestamp").set_index("timestamp")
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        for label, window in window_sizes.items():
            df[f'vol_{label}'] = df['log_return'].rolling(window).std() * annualization_factor**0.5
        return df.reset_index()

    def add_rolling_corr(self, df, name1, name2, window_sizes):
        for label, window in window_sizes.items():
            df[f'corr_{label}'] = df[f'log_return_{name1}'].rolling(window).corr(df[f'log_return_{name2}'])
        return df

    def create_pairwise_tabs(self, df_dict, resample_hours=1, tag_suffix="", date_filter=None):
        results = {}
        pairs = list(combinations(df_dict.items(), 2))
        num_hours = resample_hours
        samples_per_day = int(24 / num_hours)
        annualization_factor = 365 * 24 / num_hours
        window_sizes = {f'{d}d': d * samples_per_day for d in self.day_counts}

        for (name1, df1), (name2, df2) in pairs:
            base1, base2 = df1.copy(), df2.copy()

            if date_filter:
                base1 = base1[(base1['timestamp'] >= date_filter[0]) & (base1['timestamp'] <= date_filter[1])]
                base2 = base2[(base2['timestamp'] >= date_filter[0]) & (base2['timestamp'] <= date_filter[1])]

            min_ts = max(base1['timestamp'].min(), base2['timestamp'].min())
            base1 = base1[base1['timestamp'] >= min_ts]
            base2 = base2[base2['timestamp'] >= min_ts]

            numeric_cols = ['close', 'volume']
            df1 = base1.set_index('timestamp')[numeric_cols].resample(f'{num_hours}h').mean().interpolate().reset_index()
            df2 = base2.set_index('timestamp')[numeric_cols].resample(f'{num_hours}h').mean().interpolate().reset_index()

            if num_hours == 2:
                df1 = df1[df1['timestamp'].dt.hour % 2 == 0]
                df2 = df2[df2['timestamp'].dt.hour % 2 == 0]

            df1['symbol'] = name1.replace('_raw', '').upper()
            df1['hr'] = df1['timestamp'].dt.hour
            df2['symbol'] = name2.replace('_raw', '').upper()
            df2['hr'] = df2['timestamp'].dt.hour

            df1_feat = self.add_features(df1[['timestamp', 'hr', 'symbol', 'close', 'volume']], num_hours, annualization_factor, window_sizes)
            df2_feat = self.add_features(df2[['timestamp', 'hr', 'symbol', 'close', 'volume']], num_hours, annualization_factor, window_sizes)

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
            merged = merged[merged['timestamp'] <= self.filtered_end]

            merged = self.add_rolling_corr(merged, key1, key2, window_sizes)

            ordered = ['timestamp',
                f'hr_{key1}', f'symbol_{key1}', f'close_{key1}', f'log_return_{key1}',
                *[f'vol_{label}_{key1}' for label in window_sizes],
                f'hr_{key2}', f'symbol_{key2}', f'close_{key2}', f'log_return_{key2}',
                *[f'vol_{label}_{key2}' for label in window_sizes],
                *[f'corr_{label}' for label in window_sizes]
            ]

            tab_name = f"{key1}_{key2}{tag_suffix}"
            results[tab_name] = merged[ordered]

        return results

    def run(self, input_path, output_path):
        self.load_data(input_path)

        if self.write_raw:
            self.tab_groups['raw'] = self.raw_sheets

        if self.write_full:
            self.tab_groups['full'] = self.create_pairwise_tabs(self.raw_sheets, resample_hours=1, tag_suffix="")

        if self.write_filtered_days:
            self.tab_groups['filtered_days'] = self.create_pairwise_tabs(
                self.raw_sheets, resample_hours=1,
                tag_suffix="_filtered", date_filter=(self.filtered_start, self.filtered_end)
            )

        if self.write_filtered_hours:
            self.tab_groups['filtered_hours'] = self.create_pairwise_tabs(
                self.raw_sheets, resample_hours=2,
                tag_suffix="_hours_filtered", date_filter=(self.filtered_start, self.filtered_end)
            )

        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for group, tabs in self.tab_groups.items():
                for name, df in tabs.items():
                    df.to_excel(writer, sheet_name=name, index=False)

        print(f"Workbook saved to: {output_path}")


# MAIN
if __name__ == '__main__':
    day_counts = [1, 3, 7]
    full_cutoff = pd.Timestamp("2025-03-31 23:00:00")
    filtered_start = pd.Timestamp("2024-01-01")
    filtered_end = full_cutoff

    output_name = f"price_study_{filtered_start:%mm_%dd_%yy}_to_{full_cutoff:%mm_%dd_%yy}"
    save_dir = r'C:\Users\ehayes\OneDrive\a-mrgn\market_data'
    input_file = "prices.xlsm"

    output_file = f"{output_name}.xlsx"

    input_path = f"{save_dir}\\{input_file}"
    output_path = f"{save_dir}\\{output_file}"

    tokens = ['sol', 'jito', 'msol']

    processor = PriceStudyProcessor(
        day_counts=day_counts,
        filtered_start=filtered_start,
        filtered_end=filtered_end,
        tokens=tokens,
        output_name=output_name,
        write_raw=False,
        write_full=False,
        write_filtered_days=True,
        write_filtered_hours=True
    )

    processor.run(input_path=input_path, output_path=output_path)
