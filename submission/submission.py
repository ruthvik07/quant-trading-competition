from __future__ import annotations

# --- Participant Imports ---
# These modules are mocked by the evaluator_lambda.py and will only
# be available when running inside the Lambda environment.
try:
    from pricing.Market import Market
    from pricing.Portfolio import Portfolio
except ImportError:
    print("Failed to import backtest modules. Are you running locally?")
    # Define dummy classes for local linting/type-checking if needed
    class Market: pass
    class Portfolio: pass

# --- Setup Logger ---
import logging
import pandas as pd
logger = logging.getLogger("local_eval")

# --- Define the Trader ---
# This object will be instantiated by the factory function
class TestTrader:
    """
    Here you will define your trading strategy. 

    The TestTrader provides a simple example strategy that:
    - BUYS INTERESTingProduct if it sees the price < 3.0 and has no position.
    - SELLS INTERESTingProducts if it sees the price > 4.5 and has a position.
    """
    def __init__(self) -> None:
        logger.debug("TestTrader initialized.")
        # You can add more initialization logic here if needed.

    def on_quote(self, market: Market, portfolio: Portfolio) -> None:
        """
        This is the main event loop called by the evaluator.
        """
        
        #--- INTERESTingProduct Logic ---
        product = "INTERESTingProduct"

        # Check if we already have a position
        has_long_position = product in portfolio.positions and portfolio.positions[product] > 0
        has_short_position = product in portfolio.positions and portfolio.positions[product] < 0

        price = market.quotes[product]['price']

        # BUY Logic
        if not has_long_position and price < 3.0:
            portfolio.buy(product, 10000)

        # SELL Logic
        elif not has_short_position and price > 4.5:
            portfolio.sell(product, 10000)


        #--- James_Fund_007 Logic ---
        product = "James_Fund_007"

        has_long_position = product in portfolio.positions and portfolio.positions[product] > 0 

        if not has_long_position:
            portfolio.buy(product, 1000)


        # logger.debug(portfolio)  # this will log the total portfolio state

class Trader:
    def __init__(self, window: int = 10):
        self.window = window
        self.history = []  
        self.has_position = False  

    def on_quote(self, market: Market, portfolio: Portfolio):
        # aktuelle Preise
        quote_interest = market.quotes["INTERESTingProduct"]["price"]
        quote_fund = market.quotes["James_Fund_007"]["price"]

        # save interest in list
        self.history.append(quote_interest)

        # genug Daten gesammelt?
        if len(self.history) < self.window:
            return
        gap = 5
        # Pandas-Serie für Moving Average-Berechnung
        df = pd.Series(self.history)
        mean_total_interest = df.expanding().mean().iloc[-1]
        rolling_mean_interest = df.rolling(window=self.window).mean().iloc[-1]
        rolling_mean_before = df.rolling(window=self.window).mean().iloc[-1-gap] 
    
        if mean_total_interest < rolling_mean_interest and mean_total_interest > rolling_mean_before:
            if len(self.history)> 300:
                portfolio.buy("James_Fund_007", quantity=1000)
            else:
                portfolio.buy("James_Fund_007", quantity=10)
        elif mean_total_interest > rolling_mean_interest and mean_total_interest < rolling_mean_before:
            if len(self.history)> 300:
                portfolio.sell("James_Fund_007", quantity=1000)
            else:
                portfolio.sell("James_Fund_007", quantity=10)
        elif mean_total_interest < rolling_mean_interest:
            portfolio.buy("James_Fund_007", quantity=(10*   abs(rolling_mean_interest-mean_total_interest)))
        elif mean_total_interest > rolling_mean_interest:
            portfolio.sell("James_Fund_007", quantity=(10*abs(rolling_mean_interest-mean_total_interest)))

# --- Define the Factory Function ---
# The evaluator_lambda.py will call this function!
def build_trader() -> Trader:
    """
    Factory function to build and return the trader instance.
    """
    return Trader()