#!/usr/bin/env python
import sys
import warnings
import os

from datetime import datetime

from stock_analyzer.crew import StockAnalyzer

from dotenv import load_dotenv

load_dotenv(override=True)

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'stock': 'AAPL',  # Replace with the stock symbol you want to analyze
    }
    
    try:
        result = StockAnalyzer().crew().kickoff(inputs=inputs)

        # Print the result
        print("\n\n=== FINAL ADVICE ===\n\n")
        print(result.raw)
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def analyze_stock(stock_symbol: str) -> str:
    """
    Run the crew with the given stock symbol and return the result.
    """
    inputs = {'stock': stock_symbol}
    try:
        result = StockAnalyzer().crew().kickoff(inputs=inputs)
        # Ensure output directory exists
        advice_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../output"))
        os.makedirs(advice_dir, exist_ok=True)
        advice_path = os.path.join(advice_dir, "investment_advice.md")
        with open(advice_path, "w") as f:
            f.write(result.raw)
        return result.raw
    except Exception as e:
        return f"An error occurred while running the crew: {e}"
