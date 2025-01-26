import subprocess
from pydantic import BaseModel
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai import LLM
from typing import List

gpt_4o_mini = LLM(model="azure/gpt-4o-mini", api_version="2024-05-01-preview")

from crewai_tools import FileWriterTool


@CrewBase
class JarvisCrew:

    @agent
    def developer(self) -> Agent:
        return Agent(
            config=self.agents_config["developer"],
            llm=gpt_4o_mini,
        )

    @agent
    def diagrammer(self) -> Agent:
        return Agent(
            config=self.agents_config["diagrammer"],
            llm=gpt_4o_mini,
        )

    @task
    def generate_code(self) -> Task:
        return Task(
            config=self.tasks_config["generate_code"],
            output_pydantic=JarvisCode,
        )

    @task
    def generate_diagram(self) -> Task:
        return Task(
            config=self.tasks_config["generate_diagram"],
            output_pydantic=JarvisDiagram,
        )

    @crew
    def development_team(self) -> Crew:
        return Crew(
            agents=[self.developer()],
            tasks=[self.generate_code()],
            process=Process.sequential,
            verbose=True,
        )

    @crew
    def diagrammer_team(self) -> Crew:
        return Crew(
            agents=[self.diagrammer()],
            tasks=[self.generate_diagram()],
            process=Process.sequential,
            verbose=True,
        )


class JarvisCode(BaseModel):
    code: str
    text: str


class JarvisDiagram(BaseModel):
    diagram_code: str
    diagram_text: str
