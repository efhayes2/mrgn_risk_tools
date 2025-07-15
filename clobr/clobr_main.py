import requests

from clobr_depth_ingest import parse_market_depth
from utils.database_writer import DatabaseWriter
from utils.tokenDict import get_token_address_from_name, token_name_to_address_dict, get_token_name_to_address_dict
from utils_clobr import clobr_api_key


def fetch_market_depth(token_address: str, api_key: str) -> dict:
    """
    Fetches order book depth for a specific token address using CLOBr.

    Args:
        token_address (str): SPL token mint address (e.g., mSOL, JitoSOL)
        api_key (str): Your CLOBr API key

    Returns:
        dict: CLOBr market depth response
    """
    url = "https://clobr.io/api/v1/market-depth"
    headers = {
        "x-api-key": api_key
    }
    params = {
        "token_address": token_address
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=(5,120))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching depth for {token_address}: {e}")
        return {}


def run():
    """
    Main function to fetch and parse market depth for a specific token.
    """
    # Example token name and address
    # clobr_api_key = "clobr_87a562f447ad71236ad6ee96dd8535d7a12a0f794f083ee2"

    tokens_dict = get_token_name_to_address_dict()
    writer = DatabaseWriter(server="Quantum-PC1\\SQLEXPRESS", database="margin_1")
    api_key = clobr_api_key
    for token_name, token_address in tokens_dict.items():
        print(f"Fetching market depth for {token_name} ({token_address})...")
        depth_data = fetch_market_depth(token_address, api_key)

        if "depth_data" in depth_data:
            parse_market_depth(depth_data, writer, token=token_name)
        else:
            print(f"No depth data found for {token_name}.")

# api_key1 = clobr_api_key
# # token_name = 'mSOL'
# # token_name = 'CLOUD'
# token_name = 'dfdvSol'
# token_address1 = get_token_address_from_name(token_name)
# token_address1 = "9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump"  # mSOL

# depth_data = fetch_market_depth(token_address1, api_key1)
#
# writer = DatabaseWriter(server="Quantum-PC1\\SQLEXPRESS", database="margin_1")
# if "depth_data" in depth_data:
#     parse_market_depth(depth_data, writer, token=token_name)

if __name__ == "__main__":
    run()
    temp = 1
