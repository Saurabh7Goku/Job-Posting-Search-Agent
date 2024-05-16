import os
from crewai import Crew
from langchain_openai import ChatOpenAI
from job_manager import append_event
from task import CompanyResearchTasks
from agent import CompanyResearchAgents
from langchain_google_genai import ChatGoogleGenerativeAI


class CompanyResearchCrew:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.crew = None
        self.llm = ChatGoogleGenerativeAI(
                model = 'gemini-pro',
                verbose = True,
                temperature = 0.1,
                google_api_key= '',
            )

    def setup_crew(self, companies: list[str], positions: list[str]):
        agents = CompanyResearchAgents()
        tasks = CompanyResearchTasks(
            job_id=self.job_id)

        research_manager = agents.research_manager(
            companies, positions)
        # company_job_url_agent = agents.company_job_url_checker_agent()
        company_research_agent = agents.company_research_agent()


        company_research_tasks = [
            tasks.company_research(company_research_agent, company, positions)
            for company in companies
        ]

        manage_research_task = tasks.manage_research(
            research_manager, companies, positions, company_research_tasks)

        self.crew = Crew(
            agents=[research_manager, company_research_agent],
            tasks=[*company_research_tasks, manage_research_task],
            verbose=2,
        )

    def kickoff(self):
        if not self.crew:
            append_event(self.job_id, "Crew not set up")
            return "Crew not set up"

        append_event(self.job_id, "Task Started")
        try:
            results = self.crew.kickoff()
            append_event(self.job_id, "Task Complete")
            return results
        except Exception as e:
            append_event(self.job_id, f"An error occurred: {e}")
            return str(e)