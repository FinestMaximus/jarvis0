from anthropic import BaseModel
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from crewai import LLM

gpt_4o_mini = LLM(model="azure/gpt-4o-mini", api_version="2024-05-01-preview")


@CrewBase
class JarvisCrew:

    @agent
    def python_developer(self) -> Agent:
        return Agent(
            config=self.agents_config["python_developer"],
            llm=gpt_4o_mini,
        )

    @agent
    def code_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config["code_reviewer"],
            llm=gpt_4o_mini,
        )

    @task
    def get_python_code(self) -> Task:
        return Task(
            config=self.tasks_config["get_python_code"],
            output_pydantic=JarvisPythonCode,
        )

    @task
    def code_review(self) -> Task:
        return Task(
            config=self.tasks_config["code_review"],
            output_pydantic=JarvisPythonCode,
        )

    @crew
    def python_developement_team(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )


class JarvisPythonCode(BaseModel):
    python_code: str
