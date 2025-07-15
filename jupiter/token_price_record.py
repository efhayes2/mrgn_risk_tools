from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class TokenPriceRecord:
    symbol: str
    price: float
    lastSellPrice: float
    lastSellAt: int
    lastBuyPrice: float
    lastBuyAt: int
    buyQuotedPrice: float
    buyQuotedAt: int
    sellQuotedPrice: float
    sellQuotedAt: int
    confidenceLevel: str
    buyImpactDepth10: Optional[float]
    buyImpactDepth100: Optional[float]
    buyImpactDepth1000: Optional[float]
    sellImpactDepth10: Optional[float]
    sellImpactDepth100: Optional[float]
    sellImpactDepth1000: Optional[float]

    @staticmethod
    def from_extra_info(symbol: str, price: float, extra: Dict) -> "TokenPriceRecord":
        def safe_float(val):
            return float(val) if val is not None else float('nan')

        return TokenPriceRecord(
            symbol=symbol,
            price=price,
            lastSellPrice=safe_float(extra["lastSwappedPrice"].get("lastJupiterSellPrice")),
            lastSellAt=extra["lastSwappedPrice"].get("lastJupiterSellAt", 0),
            lastBuyPrice=safe_float(extra["lastSwappedPrice"].get("lastJupiterBuyPrice")),
            lastBuyAt=extra["lastSwappedPrice"].get("lastJupiterBuyAt", 0),
            buyQuotedPrice=safe_float(extra["quotedPrice"].get("buyPrice")),
            buyQuotedAt=extra["quotedPrice"].get("buyAt", 0),
            sellQuotedPrice=safe_float(extra["quotedPrice"].get("sellPrice")),
            sellQuotedAt=extra["quotedPrice"].get("sellAt", 0),
            confidenceLevel=extra.get("confidenceLevel", "unknown"),
            buyImpactDepth10=safe_float(extra["depth"]["buyPriceImpactRatio"]["depth"].get("10")),
            buyImpactDepth100=safe_float(extra["depth"]["buyPriceImpactRatio"]["depth"].get("100")),
            buyImpactDepth1000=safe_float(extra["depth"]["buyPriceImpactRatio"]["depth"].get("1000")),
            sellImpactDepth10=safe_float(extra["depth"]["sellPriceImpactRatio"]["depth"].get("10")),
            sellImpactDepth100=safe_float(extra["depth"]["sellPriceImpactRatio"]["depth"].get("100")),
            sellImpactDepth1000=safe_float(extra["depth"]["sellPriceImpactRatio"]["depth"].get("1000")),
        )
