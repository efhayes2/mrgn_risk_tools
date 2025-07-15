def get_token_address_from_name(name):
  return token_name_to_address_dict[name] if name in token_name_to_address_dict else None


def get_token_name_from_address(address):
    return token_address_to_name_dict[address] if address in token_address_to_name_dict else None

def get_token_name_to_address_dict():
    return token_name_to_address_dict

def get_token_address_to_name_dict():
    return token_address_to_name_dict


token_address_to_name_dict = {
    "BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85": "BNSOL",
    "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B": "bbSOL",
    "BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs": "bonkSOL",
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1": "bSOL",
    "CLoUDKc4Ane7HeQcPpE3YHnznRxhMimJ4MyaUqyHFzAu": "CLOUD",
    "Comp4ssDzXcLeu2MnLuGNNFC4cmLPMng8qWHPvzAMU1h": "compassSOL",
    "ezSoL6fY1PVdJcJsUpe5CM3xkfmy3zoVCABybm5WtiC": "ezSOL",
    "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A": "hSOL",
    "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm": "INF",
    "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn": "JitoSOL",
    "7Q2afV64in6N6SeZsAAB81TJzwDoD6zpqmHkzi9Dcavn": "JSOL",
    "jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC": "jucySOL",
    "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v": "jupSOL",
    "LSTxxxnJzKDFSLr4dUkPcmCf5VyryEqzPLz5j4bpxFp": "LST",
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": "mSOL",
    "picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX": "picoSOL",
    "So11111111111111111111111111111111111111112": "SOL"
}



token_name_to_address_dict = {
    "BNSOL": "BNso1VUJnh4zcfpZa6986Ea66P6TCp59hvtNJ8b1X85",
    "CLOUD": "CLoUDKc4Ane7HeQcPpE3YHnznRxhMimJ4MyaUqyHFzAu",
    "INF": "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",
    "JSOL": "7Q2afV64in6N6SeZsAAB81TJzwDoD6zpqmHkzi9Dcavn",
    "JitoSOL": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",
    "LST": "LSTxxxnJzKDFSLr4dUkPcmCf5VyryEqzPLz5j4bpxFp",
    "SOL": "So11111111111111111111111111111111111111112",
    "bSOL": "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",
    "bbSOL": "Bybit2vBJGhPF52GBdNaQfUJ6ZpThSgHBobjWZpLPb4B",
    "bonkSOL": "BonK1YhkXEGLZzwtcvRTip3gAL9nCeQD7ppZBLXhtTs",
    "compassSOL": "Comp4ssDzXcLeu2MnLuGNNFC4cmLPMng8qWHPvzAMU1h",
    "dfdvSol": "sctmB7GPi5L2Q5G9tUSzXvhZ4YiDMEGcRov9KfArQpx",
    "ezSOL": "ezSoL6fY1PVdJcJsUpe5CM3xkfmy3zoVCABybm5WtiC",
    "hSOL": "he1iusmfkpAdwvxLNGV8Y1iSbj4rUy6yMhEA3fotn9A",
    "jucySOL": "jucy5XJ76pHVvtPZb5TKRcGQExkwit2P5s4vY8UzmpC",
    "jupSOL": "jupSoLaHXQiZZTSfEWMTRRgpnyFm8f6sZdosWBjx93v",
    "mSOL": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "picoSOL": "picobAEvs6w7QEknPce34wAE4gknZA9v5tTonnmHYdX"
}
