# import asyncio
# from solana.rpc.async_api import AsyncClient
# from solana.publickey import PublicKey
# from pyserum.market import Market
#
#
# async def main():
#     """
#     Connects to the Solana blockchain, loads an OpenBook market,
#     and fetches the top 10 bids and asks from its order book.
#     """
#     # Define the necessary public keys
#     market_address = PublicKey("8BnEgHoWFysVcuFFX7QztDmzuH8r5ZFvyP3sYwn1XTh6")  # SOL/USDC market
#     rpc_url = "https://api.mainnet-beta.solana.com"
#
#     try:
#         # Establish an async connection to the Solana RPC endpoint
#         async with AsyncClient(rpc_url) as connection:
#
#             # Load the market state using its address
#             print(f"Loading market: {market_address}")
#             market = await Market.load(connection, market_address)
#
#             # Load the bid and ask order books
#             print("Fetching bids and asks...")
#             bids = await market.load_bids()
#             asks = await market.load_asks()
#
#             # --- Display Bids (Highest first) ---
#             print("\n--- Top 10 Bids ---")
#             print(f"{'Price':<12} {'Size':<12}")
#             print("-" * 24)
#             # The bids book is descending, so we take the first 10 items
#             for bid in list(bids)[:10]:
#                 print(f"{bid.info.price:<12.4f} {bid.info.size:<12.4f}")
#
#             # --- Display Asks (Lowest first) ---
#             print("\n--- Top 10 Asks ---")
#             print(f"{'Price':<12} {'Size':<12}")
#             print("-" * 24)
#             # The asks book is ascending, so we take the first 10 items
#             for ask in list(asks)[:10]:
#                 print(f"{ask.info.price:<12.4f} {ask.info.size:<12.4f}")
#
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
# if __name__ == "__main__":
#     asyncio.run(main())