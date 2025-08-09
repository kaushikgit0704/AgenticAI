from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from stock_analyzer_gemini.tools.custom_tool import StockAnalyzerTool, StockPriceTool
from typing import List
from pydantic import BaseModel
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

class StockPriceToolOutput(BaseModel):
    stock: str
    currentprice: str
    fiftytwoweekhigh: str
    fiftytwoweeklow: str
    recentclosingprice: str

class StockAnalyzerToolOutput(BaseModel):   
    stock: str
    currentprice: str
    avgreturn: str  
    volatility: str
    sma_50: str
    rsi: str

@CrewBase
class StockAnalyzerGemini():
    """StockAnalyzerGemini crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def market_researcher(self) -> Agent:
        #print("market_researcher model:", self.agents_config['market_researcher'])
        return Agent(
            config=self.agents_config['market_researcher'],
            verbose=True,
            tools=[StockPriceTool()],
        )

    @agent
    def performance_analyst(self) -> Agent:
        #print("performance_analyst model:", self.agents_config['performance_analyst'])
        return Agent(
            config=self.agents_config['performance_analyst'],
            verbose=True,
            tools=[StockAnalyzerTool()],
        )
    
    @agent
    def advisor(self) -> Agent:
        #print("advisor model:", self.agents_config['advisor'])
        return Agent(
            config=self.agents_config['advisor'],
            verbose=True,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def market_research(self) -> Task:
        return Task(
            config=self.tasks_config['market_research'], # type: ignore[index]
            output_pydantic=StockPriceToolOutput,  # Specify the output schema
            output_file='output/market_research.md'  # Specify the output file
        )

    @task
    def performance_analysis(self) -> Task:
        return Task(
            config=self.tasks_config['performance_analysis'], # type: ignore[index]
            output_pydantic=StockAnalyzerToolOutput,  # Specify the output schema
            output_file='output/performance_analysis.md'  # Specify the output file
        )
    
    @task
    def investment_advice(self) -> Task:
        return Task(
            config=self.tasks_config['investment_advice'], # type: ignore[index]            
            output_file='output/investment_advice.md'  # Specify the output file
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockAnalyzer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
