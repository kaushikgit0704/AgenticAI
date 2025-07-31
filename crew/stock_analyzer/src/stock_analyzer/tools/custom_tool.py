from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import yfinance as yf
import numpy as np


class StockPriceToolInput(BaseModel):
    """Input schema for MyCustomTool."""
    symbol: str = Field(..., description="Stock symbol to fetch the price for, e.g., 'AAPL' for Apple Inc.")

class StockPriceToolOutput(BaseModel):
    stock: str
    currentprice: str
    fiftytwoweekhigh: str
    fiftytwoweeklow: str
    recentclosingprice: str

class StockAnalyzerToolInput(BaseModel):    
    """Input schema for StockAnalyzerTool."""
    stock_symbol: str = Field(..., description="The stock symbol to analyze, e.g., 'AAPL' for Apple Inc.")

class StockAnalyzerToolOutput(BaseModel):   
    stock: str
    currentprice: str
    avgreturn: str  
    volatility: str
    sma_50: str
    rsi: str

class StockPriceTool(BaseTool):
    name: str = "StockPriceTool"
    description: str = "Fetches the current stock price for a given stock symbol."
    args_schema: Type[BaseModel] = StockPriceToolInput

    def _run(self, symbol: str) -> str:
        # Here you would implement the logic to fetch the stock price
        stock = yf.Ticker(symbol)
        history = stock.history(period="6mo")
        recent = stock.info
        fiftytwoweekhigh = recent.get('fiftyTwoWeekHigh', 'N/A')
        fiftytwoweeklow = recent.get('fiftyTwoWeekLow', 'N/A')
        return StockPriceToolOutput(
            stock=symbol,
            currentprice=str(recent.get('currentPrice', 'N/A')),
            fiftytwoweekhigh=str(fiftytwoweekhigh),
            fiftytwoweeklow=str(fiftytwoweeklow),
            recentclosingprice=str(history['Close'][-1]) if not history.empty else 'N/A'
        )

class StockAnalyzerTool(BaseTool):
    name: str = "StockAnalyzerTool"
    description: str = "Analyzes a stock's performance over the last 6 months."
    args_schema: Type[BaseModel] = StockAnalyzerToolInput

    def _run(self, stock_symbol: str) -> str:
        stock = yf.Ticker(stock_symbol)
        history = stock.history(period="6mo")
        
        if history.empty:
            return StockAnalyzerToolOutput(
                stock=stock_symbol,
                currentprice='N/A',
                avgreturn='N/A',
                volatility='N/A',
                sma_50='N/A',
                rsi='N/A'
            )
        
        current_price = history['Close'][-1]
        returns = history['Close'].pct_change().dropna()
        avg_return = np.mean(returns) * 100  # Convert to percentage
        volatility = np.std(returns) * 100  # Convert to percentage
        sma_50 = history['Close'].rolling(window=50).mean().iloc[-1]
        
        # Calculate RSI
        delta = history['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return StockAnalyzerToolOutput(
            stock=stock_symbol,
            currentprice=str(current_price),
            avgreturn=str(avg_return),
            volatility=str(volatility),
            sma_50=str(sma_50),
            rsi=str(rsi.iloc[-1]) if not rsi.empty else 'N/A'
        )