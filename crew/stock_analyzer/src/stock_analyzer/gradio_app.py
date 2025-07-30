import gradio as gr
import os

from stock_analyzer.main import analyze_stock

ADVICE_PATH = "../../output/investment_advice.md"

def show_processing():
    # Show custom processing message
    return gr.update(value="Analyzing...", visible=True)

def submit_stock(stock_symbol):
    # Run analysis and return result
    result = analyze_stock(stock_symbol)
    if result and result.strip():
        return gr.update(value=result, visible=True)
    else:
        return gr.update(value="", visible=False)

with gr.Blocks() as demo:
    with gr.TabItem("Analyze Stock"):
        stock_input = gr.Textbox(label="Enter Stock Symbol", value="", placeholder="e.g., AAPL for Apple Inc.")
        submit_btn = gr.Button("Analyze")
        result_box = gr.Textbox(label="Analysis Result", value="", lines=10, interactive=False, visible=False)

        # First show "Analyzing..." message
        submit_btn.click(
            fn=show_processing,
            inputs=None,
            outputs=result_box,
            queue=True
        )
        # Then run the actual analysis
        submit_btn.click(
            fn=submit_stock,
            inputs=stock_input,
            outputs=result_box,
            queue=True
        )

if __name__ == "__main__":
    demo.launch(share=True)