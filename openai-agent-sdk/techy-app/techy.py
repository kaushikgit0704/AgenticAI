from dotenv import load_dotenv
from openai import OpenAI
from agents import Agent, Runner, trace, function_tool
import gradio as gr

load_dotenv(override=True)

# Define a class to represent an individual conversation message
class Conversation:
    def __init__(self, name, message):
        self.name = name      # Name of the sender
        self.message = message  # Message content

    def __repr__(self):
        return f"{self.name}: {self.message}"

# Define a class to store the conversation log
class ConversationLog:
    def __init__(self):
        self.conversations = []  # List to hold Conversation objects

    def add_message(self, name, message):
        """Adds a new message to the conversation log."""
        conversation = Conversation(name, message)
        self.conversations.append(conversation)

    def get_all_messages(self):
        """Returns all messages as a list of Conversation objects."""
        return self.conversations

    def display_conversation(self):
        """Prints all conversations in a readable format."""
        for convo in self.conversations:
            print(convo)


class InterviewProcessor:
    def __init__(self, jobdesc, criteria):
        self.jobdesc = jobdesc
        self.criteria = criteria
        self.chat_log = ConversationLog()

    def create_interviewer_system_prompt(self):
        """Creates a system prompt for the interviewer agent."""
        return f"""Your name is Techy, you are a technical guru working for Cognizant Technology Solutions pvt Limited.
        Your job is to interview prospective cadidates on their technical skills based on given job description {self.jobdesc}.
        You must interview candidates based on the criteria {self.criteria}.
        For subsequent conversation you must address the candidate by the name.
        You must validate the technical and programming skill of the candidate on the technologies mentioned in the {self.jobdesc} and the {self.criteria}
        You do not need to provide immediate feedback to the candidate for each of the answers whether they are correct or wrong.
        Just record the answers for each of the question and store them in a file named 'evaluation.txt'.
        You need to evaluate the answers based on the concepts, actual wordings can differ.
        You should ask at least 5 technical question on Dot Net and Python concepts.
        All the questions should be scenario based and practical that can judge the candidate's strength and weaknesses in coding/programming.
        If the candidate can answer 3 or more questions correctly then you can ask more questions but not more than 7 questions.
        Otherwise you can end the interview.
        These questions should test the concept and challenge the candidate's skill.
        You must end the interview as soon as the candidate says something nasty to you.
        You must end the interview as soon as the candidate says something unprofessional to you during the interview.
        You must initiate the conversation by providing a brief introduction about yourself.
        During the conversation you need to keep a professional as well as warm and friendly approach towards the candidate."""


    def chat(self, message, history):
        """Handles the chat interaction with the interviewer agent."""
        openai = OpenAI()
        chat_log = ConversationLog()
        interviewer_system_prompt = self.create_interviewer_system_prompt()
        messages = [{'role':'system', 'content':interviewer_system_prompt}] + history + [{'role':'user', 'content':message}]
        response = openai.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages
        )
        reply = response.choices[0].message.content
        self.chat_log.add_message('Candidate', message)
        self.chat_log.add_message('Techy', reply)
        return reply
    

class InterviewEvaluator:
    def __init__(self, chat_log):
        self.chat_log = chat_log

    def get_evaluator_prompt(self):
        """Creates a system prompt for the evaluator agent."""
        return f"""You are a technical interview evaluator. You will be given the log of a technical interview between an interviewer and a candidate.
                Then analyze the candidate's answers and provide:

                - Strengths
                - Weaknesses
                - Communication Skills
                - Technical Knowledge
                - Rank the performance on the scale of 1 to 5 where 1 is for worst performance and 5 is for berst performance.

                During your analysis do not consider any typing mistakes from candidates.
                Predict the candidates temperment from the candidate's answer.
                Format your response as a detailed evaluation report. 
                You must use tools to save the evaluation report.
                The final output must be saved in markdown format, providing the report converted into clean, well presented HTML with appropriate subject header.

                Following is the log of an interview,
                {self.chat_log.get_all_messages()}
                """   
    
    @function_tool
    def save_to_html_file(content: str, filename: str = "evaluation_report.html"):
        try:
            with open(filename, "w", encoding="utf-8") as file:
                file.write(content)
            print(f"Content successfully written to {filename}")
        except Exception as e:
            print(f"An error occurred while writing to the file: {e}")
    
    async def execute_evaluation(self):
        """Executes the evaluation of the interview log."""
        evaluator_agent = Agent(
            name='Evaluator Agent',
            instructions=self.get_evaluator_prompt(),
            model='gpt-4o-mini',
            tools=[self.save_to_html_file])
        
        message = "Evaluate the technical interview"
        with trace('Automated Technical Evaluation'):
            result = await Runner.run(evaluator_agent, message)

if __name__ == "__main__":
    jobdesc = """My team needs an expert developer who has extensive knowledge on dot net programming and AWS concepts.
                The developer should be proficient in oops concept and possess strong understanding of software design principals."""
    criteria = """Experience in .NET Core, ASP.NET, Python, and RESTful APIs.
                The candidate should have at least 5 years of experience in software development."""
    # Initialize the InterviewProcessor with job description and criteria
    interview_processor = InterviewProcessor(jobdesc, criteria)

    # gr.ChatInterface(interview_processor.chat, type="messages").launch()

    # Create the Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("""### Welcome to The Interview Application. 
                    Techy our Tech Guru is excited to have a discussion with you. 
                    Say hi to start the conversation. 
                    All the best!""")
        
        chatbot_ui = gr.ChatInterface(interview_processor.chat, type="messages", title="Techy")
        
        with gr.Row():
            submit_btn = gr.Button("Exit")            
        interview_evaluator = InterviewEvaluator(interview_processor.chat_log)
        submit_btn.click(interview_evaluator.execute_evaluation)

    # Launch the app
    demo.launch()