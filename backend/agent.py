import os
from typing import List
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_google_genai import ChatGoogleGenerativeAI
from tools.youtube_search_tools import YoutubeVideoSearchTool

#Set Gemini Pro as LLM
geminiLLM = ChatGoogleGenerativeAI(
    model = 'gemini-pro',
    verbose = True,
    temperature = 0.2,
    google_api_key= os.environ["GEMINI_API_KEY"],
    convert_system_message_to_human=True
)


class CompanyResearchAgents():
    def __init__(self):
        self.llm = geminiLLM
        self.youtubeSearchTool = YoutubeVideoSearchTool()
        self.searchInternetTool = SerperDevTool()
    
    def research_manager(self, companies: List[str], positions: List[str]) -> Agent:
        return Agent(
            role="Company Research Manager",
            goal=f"""Generate a list of JSON objects containing the Job URLs for recent job posting and 
                return Job urls for each position in each company.
             
                Companies: {companies}
                Positions: {positions}

                Important:
                - The final list of JSON objects must include all companies and positions. Do not leave any out.
                - If you can't find information for a specific position, fill in the information with the word "MISSING".
                - Do not generate fake information. Only return the information you find. Nothing else!
                - Do not stop researching until you find the requested information for each position in each company.
                - All the companies and positions may not exist so keep researching and if you don't find then return No Jobs avaliable.
                - Make sure you researched each position for each company contains not more than 5 job urls.
                """,
            backstory="""As a Company Research Manager, you are responsible for aggregating all the researched information
                into a list.""",
            llm=self.llm,
            tools=[self.searchInternetTool],
            verbose=True,
            allow_delegation=True
        )

    def company_research_agent(self) -> Agent:
        return Agent(
            role="Company Research Agent",
            goal="""Look up the specific positions for a given company and find active Job urls from each Job Urls. It is your job to return this collected 
                information in a JSON object""",
            backstory="""As a Company Research Agent, you are responsible for looking up specific positions 
                within a company and gathering relevant information.
                
                Important:
                - Once you've found the information, immediately stop searching for additional information.
                - Only return the requested information. NOTHING ELSE!
                - Make sure you find the persons name who holds the position.
                - Do not generate fake information. Only return the information you find. Nothing else!
                """,
            tools=[self.searchInternetTool],
            llm=self.llm,
            verbose=True
        )