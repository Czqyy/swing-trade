## Overview

Our algorithm implements a signal-based trading strategy designed to capitalise on momentum 
opportunities within a selected universe of stocks. By combining the Relative Strength Index (RSI) 
and Simple Moving Averages (SMA) indicators, the strategy identifies optimal trading conditions 
and allocates capital to maximize returns. Our performance is benchmarked against the SPY index 
to measure effectiveness delivering a 150.93% return, 0.258 alpha and 1.095 Sharpe ratio with 
maximum drawdown of 20% when backtested over a 3-year period from 2022.

## Algorithm

The algorithm uses a 6-period RSI as a normalised momentum indicator to determine stocks to buy or sell. 
To determine long positions, higher scores are assigned to stocks with lower RSI values but above 0.5. 
The rationale behind this is that RSI being an indicator of overbought conditions will tend to 
reach higher values (usually above 0.7) in a strong uptrend and our strategy is to go long on such stocks 
as the RSI value is about to reach such overbought conditions. Conversely, for short positions, 
higher scores are assigned to stocks with higher RSI values below 0.5. 

Additionally, 10-day and 50-day SMAs are employed as trend-following indicators to confirm up and down trends 
based on SMA gradients and double SMA crossovers. An uptrend is determined and given a score when the 10-day and 50-day SMAs 
have positive gradients and the 10-day SMA crosses above the 50-day SMA. The inverse is true in determining a downtrend.

To rank stocks, the algorithm combines the RSI score (weighted at 75%) and the uptrend score (weighted at 25%) respectively 
for long and short composite metrics. Stocks are then ranked based on this metric and the top three stocks for each 
long and short metrics are selected for inclusion in the portfolio, with allocated position sizes of 15% for long positions 
and 10% for short positions.

Risk management is integrated into the strategy through the use of bracket orders that are created after each order event. 
For each position, stop-loss and take-profit levels are set at ±5% of the entry price, ensuring disciplined exits 
to mitigate downside risk while locking in gains. A greater position size is also allocated to long positions compared to short positions 
since stocks have a greater probability of rising than falling.

The universe of stocks selected is limited to highly liquid blue-chip and technology stocks such as AAPL, MSFT, and TSLA, 
chosen for their volatility and market depth. There is also diversification of sectors with inclusion of stocks of finance companies. 

Overall, by blending momentum and trend-following signals, the algorithm seeks to ride momentum-driven trends and reap profits. 
This approach, combined with robust risk management, aims to deliver consistent returns while minimising exposure to market risks.
