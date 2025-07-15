from jupiter.token_price_record import TokenPriceRecord
from utils.utils import safe_float, safe_int
from datetime import datetime
from typing import List
import pandas as pd
import pyodbc

# db_writer = DatabaseWriter(server="Quantum-PC1\\SQLEXPRESS", database="margin_1")
class DatabaseWriter:
    def __init__(self, server="Quantum-PC1\\SQLEXPRESS", database="margin_1"):
        self.cursor = None
        self.conn = None
        self.connection_string = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={server};'
            f'DATABASE={database};'
            f'Trusted_Connection=yes;'
        )
        self.connect()

    def connect(self):
        self.conn = pyodbc.connect(self.connection_string)
        self.cursor = self.conn.cursor()

    # def insert_into_market_depth(self, df: pd.DataFrame):
    #     cursor = self.conn.cursor()
    #     for _, row in df.iterrows():
    #         cursor.execute("""
    #             INSERT INTO MarketDepth (token_name, timestamp, price, support, support_amount, resistance, resistance_amount)
    #             VALUES (?, ?, ?, ?, ?, ?, ?)
    #         """, row.token_name, row.timestamp, row.price,
    #              row.support, row.support_amount,
    #              row.resistance, row.resistance_amount)
    #     self.conn.commit()

    def insert_into_slippage_buckets(self, df: pd.DataFrame):
        cursor = self.conn.cursor()
        for _, row in df.iterrows():
            cursor.execute("""
                           INSERT INTO SlippageBuckets (token, market_price, timestamp, bp_from_mid,
                                                        bucket_price, support_in_bucket, cumulative_support,
                                                        resistance_in_bucket, cumulative_resistance)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                           """, row.token, row.market_price, row.timestamp, row.bp_from_mid,
                           row.bucket_price,
                           row.support_in_bucket, row.cumulative_support,
                           row.resistance_in_bucket, row.cumulative_resistance)
        self.conn.commit()



    def insert_into_token_price_records(self, record: TokenPriceRecord):
        query = '''
            INSERT INTO TokenPriceRecords (
                symbol, price, lastSellPrice, lastSellAt, lastBuyPrice, lastBuyAt,
                buyQuotedPrice, buyQuotedAt, sellQuotedPrice, sellQuotedAt,
                confidenceLevel,
                buyImpactDepth10, buyImpactDepth100, buyImpactDepth1000,
                sellImpactDepth10, sellImpactDepth100, sellImpactDepth1000,
                updatedAt
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        '''

        now = datetime.now()
        args = (
            record.symbol,
            safe_float(record.price),
            safe_float(record.lastSellPrice),
            safe_int(record.lastSellAt),
            safe_float(record.lastBuyPrice),
            safe_int(record.lastBuyAt),
            safe_float(record.buyQuotedPrice),
            safe_int(record.buyQuotedAt),
            safe_float(record.sellQuotedPrice),
            safe_int(record.sellQuotedAt),
            record.confidenceLevel,
            safe_float(record.buyImpactDepth10),
            safe_float(record.buyImpactDepth100),
            safe_float(record.buyImpactDepth1000),
            safe_float(record.sellImpactDepth10),
            safe_float(record.sellImpactDepth100),
            safe_float(record.sellImpactDepth1000),
            datetime.now()
        )

        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            print('Symbol :', record.symbol, ': Insert succeeded.')
        except Exception as e:
            print(f"Insert failed for symbol: {record.symbol}")
            print(record.sellQuotedPrice, safe_float(record.sellQuotedPrice))
            print(record.sellImpactDepth1000, safe_float(record.sellImpactDepth1000))
            print(f"{e}")
            print()

    def insert_records(self, records: List[TokenPriceRecord]):
        for record in records:
            self.insert_into_token_price_records(record)

    def close(self):
        self.cursor.close()
        self.conn.close()
