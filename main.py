# region imports
from AlgorithmImports import *
# endregion


class Algo(QCAlgorithm):

    def initialize(self):
        self.set_start_date(2022, 1, 1)
        self.set_end_date(2024, 12, 31)
        self.set_cash(100000)

        # Basket of equities to trade
        self.symbols = ['AAPL', 'MSFT', 'GOOG', 'AMZN', 'TSLA', 'NVDA', 'JPM', 'GS', 'BAC']
        self.indicators = {}
        for symbol in self.symbols:
            self.add_equity(symbol, Resolution.Daily)
            self.indicators[symbol] = {
                'RSI': self.rsi(symbol, 6),
                'ShortSMA': self.SMA(symbol, 10, Resolution.Daily),
                "MediumSMA": self.SMA(symbol, 50, Resolution.Daily),
            }

        # Weights for rsi and trend factors
        self.weight_rsi = 0.7
        self.weight_uptrend = 0.3

        # Profit target and stop loss for each trade
        self.profit_target = 0.05
        self.stop_loss = 0.05

        self.SetWarmUp(timedelta(days=50))

        # Sets SPY as a benchmark to display our results against
        data_bench = self.add_equity("SPY", Resolution.Daily)
        self.bench_symbol = data_bench.Symbol
        self.benchmarkTicker = self.bench_symbol
        self.SetBenchmark(self.bench_symbol)
        self.initBenchmarkPrice = None
        self.BenchmarkPerformance = self.Portfolio.TotalPortfolioValue

    # Function that just sets up the benchmark  
    def UpdateBenchmarkValue(self): 
        if self.initBenchmarkPrice is None: 
            self.initBenchmarkCash = self.Portfolio.Cash 
            self.initBenchmarkPrice = self.Benchmark.Evaluate(self.Time) 
            self.benchmarkValue = self.initBenchmarkCash 
        else: 
            currentBenchmarkPrice = self.Benchmark.Evaluate(self.Time) 
            self.benchmarkValue = (currentBenchmarkPrice / self.initBenchmarkPrice) * self.initBenchmarkCash

    def on_data(self, data: Slice):
        if self.IsWarmingUp:
            return

        # Compute scores for each stock
        scores = {}
        for symbol in self.symbols:
            if not data.Bars.ContainsKey(symbol):
                continue
            
            indicators = self.indicators[symbol]
            rsi = indicators["RSI"]
            short_sma = indicators["ShortSMA"]
            medium_sma = indicators["MediumSMA"]

            # Check if indicators are ready
            if not rsi.IsReady or not short_sma.IsReady or not medium_sma.IsReady:
                continue

            # Combine scores
            trend_score = self.uptrend_score(short_sma, medium_sma)
            scores[symbol] = self.weight_rsi * self.rsi_score(rsi) + self.weight_uptrend * trend_score

        # Rank stocks by score
        ranked_stocks = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Allocate portfolio
        total_weight = 0
        for rank, (symbol, score) in enumerate(ranked_stocks):
            if total_weight >= 1.0:
                break
                
            # Dynamic weight: higher for top-ranked stocks
            weight = min(0.15, 1 / (rank + 1)) 
            self.set_holdings(symbol, weight)
            self.bracket_pending = True
            total_weight += weight

        # Liquidate stocks not in the top-ranked
        top_symbols = [symbol for symbol, score in ranked_stocks[:3]]  # Keep top 3
        for symbol in self.Portfolio.Keys:
            if symbol.Value not in top_symbols and self.Portfolio[symbol].Invested:
                self.Liquidate(symbol)

        # plotting our data:
        self.UpdateBenchmarkValue()
        self.plot('Strategy Equity', self.benchmarkTicker, self.benchmarkValue)
        self.plot('Strategy Equity', 'Portfolio', self.Portfolio.TotalPortfolioValue)

    def rsi_score(self, rsi: RelativeStrengthIndex):
        """
        Calculate normalised RSI score favouring oversold stocks
        """
        normalized_rsi = rsi.Current.Value / 100
        return 1 - normalized_rsi      # Higher score for lower RSI


    def uptrend_score(self, short_sma: SimpleMovingAverage, medium_sma: SimpleMovingAverage):
        """
        Calculates uptrend score given a short-term moving average and medium-term moving average 
        """
        # Calculate gradients
        short_sma_gradient = short_sma.window[0].Value - short_sma.window[1].Value
        medium_sma_gradient = medium_sma.window[0].Value - medium_sma.window[1].Value

        # Check for an uptrend
        gradient_positive = short_sma_gradient > 0 and medium_sma_gradient > 0
        short_above_medium = short_sma.Current.Value > medium_sma.Current.Value

        if not (gradient_positive or short_above_medium):
            return 0
        else:
            return short_sma_gradient

    
    def on_order_event(self, order_event: OrderEvent):
        """
        Place bracket order for profit target and stop loss after a market order is placed.
        """
        if order_event.status == OrderStatus.FILLED:
            symbol = order_event.Symbol
            holding = self.Portfolio[symbol]

            if self.bracket_pending and holding.invested:
                quantity = holding.quantity
                entry_price = holding.average_price

                # Calculate stop-loss and take-profit prices
                stop_loss_price = entry_price * (1 - self.stop_loss)
                profit_price = entry_price * (1 + self.profit_target)

                # Place stop-loss and take-profit orders
                self.stop_market_order(symbol, -quantity, stop_loss_price)
                self.limit_order(symbol, -quantity, profit_price)

                # Mark the bracket orders as placed
                self.bracket_pending = False
