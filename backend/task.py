import logging
from textwrap import dedent
from crewai import Task, Agent
from models import PositionInfoList, PositionInfo
from job_manager import append_event

class CompanyResearchTasks():

    def __init__(self, job_id):
        self.job_id = job_id

    def append_event_callback(self, task_output):
        logging.info("Callback called: %s", task_output)
        append_event(self.job_id, task_output.exported_output)

    def manage_research(self, agent: Agent, companies: list[str], positions: list[str], tasks: list[Task]):
        return Task(
            description=dedent(f"""Based on the list of companies {companies} and the positions {positions},
                use the results from the company_research_agent to get Job Post URLs for each position in each company.
                               
                Check the Job Post URLs in each position for each Company.
                Return this collected information in a json object containing the Job Post URLs for each position in each company ONLY.
                               
                Important:
                - Only return URLs for each position for each company, which have recent job post and still accepting job applications.
                               
                """),
            agent=agent,
            expected_output=dedent(
                """A json object only containing the Job Post URLs for each position in each company."""),
            callback=self.append_event_callback,
            context=tasks,
            output_json=PositionInfoList
        )
    
    # def company_job_url_research(self, agent: Agent, company: str, positions: list[str]):
    #     return Task(
    #         description=dedent(f"""Based on the list of companies {company} and the positions {positions},
    #             use the results from the company_research_agent to get Job Post URLs for each position in each company.
                               
    #             Find the Job Post URLs in each position for each Company.
    #             Check the URLs if the webpage containes any text like "No longer accepting applications", "Link is broken" or "Page Not Found" then don't return URLs.
    #             Return this collected information in a JSON object only.
                               
    #             Helpful Tips:
    #             - Filter out the URLs and Look for the apply button on the webpage if the company still accepting the application.
    #             - To find the active URLs launch the URLs one by one and see if the company job links still active or not. 
                               
    #             Important:
    #             - Only return URLs which have recent job post and still accepting job applications.
    #             - Once you've found the information, immediately stop searching for additional information.
    #             - Only return the requested information. NOTHING ELSE!
    #             - Do not generate fake information. Only return the information you find. Nothing else!
    #             - Do not stop researching until you find the requested information for each position in the company.
    #             """),
    #         agent=agent,
    #         expected_output="""ONLY JSON object containing the working Job Post Urls for each position in the company.""",
    #         callback=self.append_event_callback,
    #         output_json=PositionInfo,
    #     )

    def company_research(self, agent: Agent, company: str, positions: list[str]):
        return Task(
            description=dedent(f"""Research the position {positions} for the {company} company. 
                For each position, 
                               
                Find the Job Post URLs in each position for each Company.
                Return this collected information in a JSON object only.
                
                Helpful Tips:
                               
                - To find the Job Post URLs, perform searches on Google such like the following:
                    - "{company} [POSITION HERE] Career Page"
                Check the URLs if the webpage containes any text like "No longer accepting applications", "Link is broken" or "Page Not Found" then don't return URLs.

                - To find the More Job Post URLs, perform searches on LinkedIn such as the following:
                    - "{company} [POSITION HERE]"
                Check the URLs if the webpage containes any text like "No longer accepting applications", "Link is broken" or "Page Not Found" then don't return URLs.
                               
                Important:
                - Only return URLs which have recent job post not the expired one.
                - Once you've found the information, immediately stop searching for additional information.
                - Only return the requested information. NOTHING ELSE!
                - Do not generate fake information. Only return the information you find. Nothing else!
                - Do not stop researching until you find the requested information for each position in the company.
                """),

            agent=agent,
            expected_output="""A JSON object containing the researched Job Post Urls for each position in the company.""",
            callback=self.append_event_callback,
            output_json=PositionInfo,
        )