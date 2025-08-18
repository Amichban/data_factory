"""
OANDA Instrument Specifications
Contains pip values, margin requirements, and trading specifications for all supported instruments.
Data source: https://www.oanda.com/bvi-en/cfds/learn/introduction-to-leverage-trading/what-is-a-pip/
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class MarginTier:
    """Represents a margin tier with position size range and margin rate."""
    min_position: float  # Minimum position size in USD equivalent
    max_position: float  # Maximum position size in USD equivalent (None for unlimited)
    margin_rate: float   # Margin rate as decimal (e.g., 0.01 for 1%)

@dataclass
class InstrumentSpec:
    """Complete specification for a trading instrument."""
    symbol: str
    name: str
    asset_class: str
    contract_size: float
    min_trade_size: float
    pip_location: float  # Decimal places for pip (e.g., 0.0001 for 4th decimal)
    pip_value_currency: str
    pip_value_amount: float  # Value per pip
    margin_tiers: List[MarginTier]
    
    def get_margin_rate(self, position_size_usd: float) -> float:
        """Get applicable margin rate for given position size."""
        for tier in self.margin_tiers:
            if tier.min_position <= position_size_usd <= (tier.max_position or float('inf')):
                return tier.margin_rate
        # Return highest tier if no match
        return self.margin_tiers[-1].margin_rate
    
    def calculate_pip_value(self, units: int, quote_currency_rate: float = 1.0) -> float:
        """Calculate pip value for given units."""
        # For instruments quoted in different currencies, adjust by exchange rate
        return units * self.pip_location * self.pip_value_amount * quote_currency_rate


# Define all OANDA instrument specifications
INSTRUMENT_SPECS: Dict[str, InstrumentSpec] = {
    
    # === MAJOR FX PAIRS ===
    "EUR_USD": InstrumentSpec(
        symbol="EUR_USD",
        name="Euro / US Dollar",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),      # < 2m: 0.50%
            MarginTier(2_000_000, 5_000_000, 0.01),   # 2-5m: 1.00%
            MarginTier(5_000_000, 50_000_000, 0.05),  # 5-50m: 5.00%
            MarginTier(50_000_000, None, 0.20),       # > 50m: 20.00%
        ]
    ),
    
    "GBP_USD": InstrumentSpec(
        symbol="GBP_USD",
        name="British Pound / US Dollar",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),
            MarginTier(2_000_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 50_000_000, 0.05),
            MarginTier(50_000_000, None, 0.20),
        ]
    ),
    
    "AUD_USD": InstrumentSpec(
        symbol="AUD_USD",
        name="Australian Dollar / US Dollar",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),
            MarginTier(2_000_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 50_000_000, 0.05),
            MarginTier(50_000_000, None, 0.20),
        ]
    ),
    
    "NZD_USD": InstrumentSpec(
        symbol="NZD_USD",
        name="New Zealand Dollar / US Dollar",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),
            MarginTier(2_000_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 50_000_000, 0.05),
            MarginTier(50_000_000, None, 0.20),
        ]
    ),
    
    "USD_CAD": InstrumentSpec(
        symbol="USD_CAD",
        name="US Dollar / Canadian Dollar",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="CAD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),
            MarginTier(2_000_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 50_000_000, 0.05),
            MarginTier(50_000_000, None, 0.20),
        ]
    ),
    
    "USD_CHF": InstrumentSpec(
        symbol="USD_CHF",
        name="US Dollar / Swiss Franc",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="CHF",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.005),
            MarginTier(2_000_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 50_000_000, 0.05),
            MarginTier(50_000_000, None, 0.20),
        ]
    ),
    
    "USD_JPY": InstrumentSpec(
        symbol="USD_JPY",
        name="US Dollar / Japanese Yen",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.001,
        pip_value_currency="JPY",
        pip_value_amount=1000,
        margin_tiers=[
            MarginTier(0, 500_000, 0.005),      # < 0.5m: 0.50%
            MarginTier(500_000, 5_000_000, 0.02),   # 0.5-5m: 2.00%
            MarginTier(5_000_000, 50_000_000, 0.05), # 5-50m: 5.00%
            MarginTier(50_000_000, None, 0.20),      # > 50m: 20.00%
        ]
    ),
    
    # === FX CROSS PAIRS ===
    "EUR_GBP": InstrumentSpec(
        symbol="EUR_GBP",
        name="Euro / British Pound",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="GBP",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 1_000_000, 0.0067),
            MarginTier(1_000_000, 5_000_000, 0.0133),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "EUR_JPY": InstrumentSpec(
        symbol="EUR_JPY",
        name="Euro / Japanese Yen",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.001,
        pip_value_currency="JPY",
        pip_value_amount=1000,
        margin_tiers=[
            MarginTier(0, 1_000_000, 0.0067),
            MarginTier(1_000_000, 5_000_000, 0.0133),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "EUR_CHF": InstrumentSpec(
        symbol="EUR_CHF",
        name="Euro / Swiss Franc",
        asset_class="FX",
        contract_size=100000,
        min_trade_size=0.01,
        pip_location=0.00001,
        pip_value_currency="CHF",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 1_000_000, 0.0067),
            MarginTier(1_000_000, 5_000_000, 0.0133),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    # === COMMODITIES ===
    "XAU_USD": InstrumentSpec(
        symbol="XAU_USD",
        name="Gold / US Dollar",
        asset_class="METAL",
        contract_size=100,  # 100 ounces
        min_trade_size=0.1,
        pip_location=0.001,
        pip_value_currency="USD",
        pip_value_amount=100,
        margin_tiers=[
            MarginTier(0, 1_000_000, 0.005),        # < 1m: 0.50%
            MarginTier(1_000_000, 5_000_000, 0.01), # 1-5m: 1.00%
            MarginTier(5_000_000, 20_000_000, 0.05), # 5-20m: 5.00%
            MarginTier(20_000_000, None, 0.20),      # > 20m: 20.00%
        ]
    ),
    
    "XAG_USD": InstrumentSpec(
        symbol="XAG_USD",
        name="Silver / US Dollar",
        asset_class="METAL",
        contract_size=5000,  # 5,000 ounces
        min_trade_size=0.1,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=5,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.025),        # < 2m: 2.50%
            MarginTier(2_000_000, 5_000_000, 0.04), # 2-5m: 4.00%
            MarginTier(5_000_000, 20_000_000, 0.10), # 5-20m: 10.00%
            MarginTier(20_000_000, None, 0.20),      # > 20m: 20.00%
        ]
    ),
    
    "BCO_USD": InstrumentSpec(  # UK Oil (UKOIL)
        symbol="BCO_USD",
        name="Brent Crude Oil",
        asset_class="ENERGY",
        contract_size=1000,  # 1,000 barrels
        min_trade_size=0.1,
        pip_location=0.001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 100_000, 0.01),           # < 100k: 1.00%
            MarginTier(100_000, 500_000, 0.02),     # 100k-500k: 2.00%
            MarginTier(500_000, 800_000, 0.04),     # 500k-800k: 4.00%
            MarginTier(800_000, None, 0.20),        # 800k+: 20.00%
        ]
    ),
    
    "WTICO_USD": InstrumentSpec(  # US Oil (USOIL)
        symbol="WTICO_USD",
        name="West Texas Intermediate Crude Oil",
        asset_class="ENERGY",
        contract_size=1000,  # 1,000 barrels
        min_trade_size=0.1,
        pip_location=0.001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 100_000, 0.01),
            MarginTier(100_000, 500_000, 0.02),
            MarginTier(500_000, 800_000, 0.04),
            MarginTier(800_000, None, 0.20),
        ]
    ),
    
    "NATGAS_USD": InstrumentSpec(
        symbol="NATGAS_USD",
        name="Natural Gas",
        asset_class="ENERGY",
        contract_size=10000,  # 10,000 MMBtu
        min_trade_size=0.1,
        pip_location=0.001,
        pip_value_currency="USD",
        pip_value_amount=10,
        margin_tiers=[
            MarginTier(0, 25_000, 0.01),            # < 25k: 1.00%
            MarginTier(25_000, 50_000, 0.035),      # 25k-50k: 3.50%
            MarginTier(50_000, 500_000, 0.05),      # 50k-500k: 5.00%
            MarginTier(500_000, None, 0.20),        # 500k+: 20.00%
        ]
    ),
    
    "XCU_USD": InstrumentSpec(  # Copper
        symbol="XCU_USD",
        name="Copper",
        asset_class="METAL",
        contract_size=25000,  # 25,000 lbs
        min_trade_size=0.1,
        pip_location=0.00001,
        pip_value_currency="USD",
        pip_value_amount=2.5,
        margin_tiers=[
            MarginTier(0, 2_000_000, 0.01),         # < 2m: 1.00%
            MarginTier(2_000_000, 5_000_000, 0.02), # 2-5m: 2.00%
            MarginTier(5_000_000, 20_000_000, 0.05), # 5-20m: 5.00%
            MarginTier(20_000_000, None, 0.20),      # > 20m: 20.00%
        ]
    ),
    
    # === EQUITY INDICES ===
    "SPX500_USD": InstrumentSpec(  # US500
        symbol="SPX500_USD",
        name="S&P 500",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),        # < 1.5m: 0.50%
            MarginTier(1_500_000, 5_000_000, 0.01), # 1.5-5m: 1.00%
            MarginTier(5_000_000, 20_000_000, 0.05), # 5-20m: 5.00%
            MarginTier(20_000_000, None, 0.20),      # > 20m: 20.00%
        ]
    ),
    
    "NAS100_USD": InstrumentSpec(  # US100
        symbol="NAS100_USD",
        name="NASDAQ 100",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "US30_USD": InstrumentSpec(
        symbol="US30_USD",
        name="Dow Jones Industrial Average",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "UK100_GBP": InstrumentSpec(
        symbol="UK100_GBP",
        name="FTSE 100",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="GBP",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "DE30_EUR": InstrumentSpec(  # DE40
        symbol="DE30_EUR",
        name="DAX 30",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="EUR",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "FR40_EUR": InstrumentSpec(
        symbol="FR40_EUR",
        name="CAC 40",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="EUR",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "JP225_USD": InstrumentSpec(
        symbol="JP225_USD",
        name="Nikkei 225",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=1,
        pip_location=1,
        pip_value_currency="JPY",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_500_000, 0.005),
            MarginTier(1_500_000, 5_000_000, 0.01),
            MarginTier(5_000_000, 20_000_000, 0.05),
            MarginTier(20_000_000, None, 0.20),
        ]
    ),
    
    "CN50_USD": InstrumentSpec(
        symbol="CN50_USD",
        name="China A50",
        asset_class="INDEX",
        contract_size=1,
        min_trade_size=0.1,
        pip_location=0.1,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 1_000_000, 0.0067),
            MarginTier(1_000_000, 2_000_000, 0.0133),
            MarginTier(2_000_000, 10_000_000, 0.05),
            MarginTier(10_000_000, None, 0.20),
        ]
    ),
    
    # === CRYPTOCURRENCIES ===
    "BTC_USD": InstrumentSpec(
        symbol="BTC_USD",
        name="Bitcoin",
        asset_class="CRYPTO",
        contract_size=1,
        min_trade_size=0.01,
        pip_location=0.01,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 100_000, 0.10),           # < 0.1m: 10%
            MarginTier(100_000, 200_000, 0.20),     # 0.1-0.2m: 20%
            MarginTier(200_000, None, 0.30),        # ≥ 0.2m: 30%
        ]
    ),
    
    "ETH_USD": InstrumentSpec(
        symbol="ETH_USD",
        name="Ethereum",
        asset_class="CRYPTO",
        contract_size=1,
        min_trade_size=0.01,
        pip_location=0.01,
        pip_value_currency="USD",
        pip_value_amount=1,
        margin_tiers=[
            MarginTier(0, 50_000, 0.15),            # < 0.05m: 15%
            MarginTier(50_000, 200_000, 0.25),      # 0.05-0.2m: 25%
            MarginTier(200_000, None, 0.50),        # ≥ 0.2m: 50%
        ]
    ),
}


def get_instrument_spec(symbol: str) -> InstrumentSpec:
    """Get instrument specification by symbol."""
    if symbol not in INSTRUMENT_SPECS:
        raise ValueError(f"Instrument {symbol} not found in specifications")
    return INSTRUMENT_SPECS[symbol]


def get_all_symbols() -> List[str]:
    """Get list of all available instrument symbols."""
    return list(INSTRUMENT_SPECS.keys())


def get_symbols_by_asset_class(asset_class: str) -> List[str]:
    """Get symbols filtered by asset class."""
    return [
        symbol for symbol, spec in INSTRUMENT_SPECS.items()
        if spec.asset_class == asset_class
    ]


def calculate_margin_requirement(symbol: str, units: int, current_price: float) -> Tuple[float, float]:
    """
    Calculate margin requirement for a position.
    
    Returns:
        Tuple of (margin_required, margin_rate_used)
    """
    spec = get_instrument_spec(symbol)
    
    # Calculate position value correctly based on instrument type
    if spec.asset_class == "FX":
        # For FX: units are in base currency, convert to USD
        position_value = abs(units) * current_price
    else:
        # For other instruments: units * price * contract_size
        position_value = abs(units) * current_price * spec.contract_size
    
    margin_rate = spec.get_margin_rate(position_value)
    margin_required = position_value * margin_rate
    
    return margin_required, margin_rate


def calculate_pip_value_usd(symbol: str, units: int, current_price: float, 
                           usd_conversion_rate: float = 1.0) -> float:
    """
    Calculate pip value in USD for a position.
    
    Args:
        symbol: Instrument symbol
        units: Number of units
        current_price: Current market price
        usd_conversion_rate: Conversion rate to USD if pip currency is not USD
    """
    spec = get_instrument_spec(symbol)
    pip_value = spec.calculate_pip_value(units, usd_conversion_rate)
    return pip_value