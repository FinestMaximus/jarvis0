#!/usr/bin/env python
import logging
import os
import subprocess
import streamlit as st
from pydantic import BaseModel
from crewai.flow import Flow, listen, start, router
import yaml
from crews.jarvis_crew.jarvis_crew import JarvisCrew

from interpreter import interpreter

interpreter.auto_run = True
interpreter.llm.model = "azure/gpt-4o-mini"
interpreter.safe_mode = "off"
interpreter.llm.supports_functions = True
interpreter.verbose = False


class JarvisState(BaseModel):
    instruction: str = ""
    task: str = ""  # Python, Javascript, Flutter, Diagram, PyTM
    topic: str = ""  # programming, diagraming, pytm


class JarvisFlow(Flow[JarvisState]):
    def __init__(self, initial_state: JarvisState):
        super().__init__()
        self._state = initial_state

    @start()
    def getting_started(self):
        print(
            f"""Entering getting_started method with inputs provided: 
            - {self._state.instruction}, 
            - {self._state.topic}"""
        )

    @router(getting_started)
    def routing(self):
        if self._state.topic == "python":
            return "programming"
        if self._state.topic == "javascript":
            return "programming"
        if self._state.topic == "flutter":
            return "programming"
        elif self._state.topic == "pytm":
            return "pytm"
        elif self._state.topic == "graphviz":
            return "graphviz"
        else:
            pass

    @listen("programming")
    def generate_code(self):
        try:
            inputs = {
                "instruction": self._state.instruction,
                "expertise": self._state.task,
                "language": self._state.topic,
            }

            results = JarvisCrew().development_team().kickoff(inputs=inputs)

            return results.pydantic.model_dump(), "code"

        except Exception as e:
            print(f"Error in JarvisCrew execution: {e}")
            self.results = ""

    @listen("graphviz")
    def generate_diagram(self):
        try:
            print("Initializing JarvisCrew...")
            inputs = {
                "instruction": self._state.instruction,
                "expertise": self._state.task,
                "diagram_type": self._state.topic,
            }

            results = JarvisCrew().diagrammer_team().kickoff(inputs=inputs)

            return results.pydantic.model_dump(), "graphviz"

        except Exception as e:
            print(f"Error in JarvisCrew execution: {e}")
            self.results = ""

    @listen("pytm")
    def generate_pytm(self):
        try:
            print("Initializing JarvisCrew...")
            inputs = {
                "instruction": self._state.instruction,
                "expertise": self._state.task,
                "diagram_type": self._state.topic,
            }

            results = JarvisCrew().diagrammer_team().kickoff(inputs=inputs)

            return results.pydantic.model_dump(), "pytm"

        except Exception as e:
            print(f"Error in JarvisCrew execution: {e}")
            self.results = ""


def plot():
    jarvis_flow = JarvisFlow(JarvisState())
    jarvis_flow.plot()


def main() -> None:
    st.set_page_config(layout="wide")  # Ensure the app is in wide mode

    # Initialize session state keys
    if "response" not in st.session_state:
        st.session_state["response"] = None
    if "response_type" not in st.session_state:
        st.session_state["response_type"] = None

    try:
        print("Checking if config.yaml exists")
        if not os.path.exists("config.yaml"):
            st.error("Configuration file 'config.yaml' not found.")
            print("Configuration file 'config.yaml' not found.")
            st.stop()

        print("Loading user credentials from config.yaml")
        with open("config.yaml") as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
            print(f"Config loaded: {config}")

        selected_task = st.sidebar.radio(
            "Task",
            ("Python", "Javascript", "Flutter", "Graphviz", "PyTM"),
        )

        task_mapping = {
            "Python": (
                "This task involves Python programming.",
                "python",
            ),
            "Javascript": (
                "This task involves Javascript development.",
                "javascript",
            ),
            "Flutter": (
                "This task involves Flutter app development.",
                "flutter",
            ),
            "Graphviz": (
                "This task involves creating Graphviz diagrams.",
                "graphviz",
            ),
            "PyTM": (
                """This task involves PyTM related queries. You are an expert in PyTM, a Python-based tool for creating and managing technical documents. You are able to generate PyTM code and diagrams that are both accurate and visually appealing. You are also able to generate PyTM code that is both accurate and visually appealing. You are also able to generate PyTM code that is both accurate and visually appealing. you're a pytm threat modeling expert, who only sends python code back (no other output). Based on current context // more prompting here..
                (example of a pytm threat model) build a similar file for the application described in this prompt.
                    You MUST only respond with the Python code block. See below for a simple example of the required format and syntax for your output.
                    You must also be consistent and coherent with the example below:

                      #!/usr/bin/env python3

                      from pytm import (
                          TM,
                          Actor,
                          Boundary,
                          Classification,
                          Data,
                          Dataflow,
                          Datastore,
                          Lambda,
                          Server,
                          DatastoreType,
                      )

                      tm = TM("my test tm")
                      tm.description = "This is a sample threat model of a very simple system - a web-based comment system. The user enters comments and these are added to a database and displayed back to the user. The thought is that it is, though simple, a complete enough example to express meaningful threats."
                      tm.isOrdered = True
                      tm.mergeResponses = True
                      tm.assumptions = [
                      "Here you can document a list of assumptions about the system",
                      ]

                      internet = Boundary("Internet")

                      server_db = Boundary("Server/DB")
                      server_db.levels = [2]

                      vpc = Boundary("AWS VPC")

                      user = Actor("User")
                      user.inBoundary = internet
                      user.levels = [2]

                      web = Server("Web Server")
                      web.OS = "Ubuntu"
                      web.controls.isHardened = True
                      web.controls.sanitizesInput = False
                      web.controls.encodesOutput = True
                      web.controls.authorizesSource = False
                      web.sourceFiles = ["pytm/json.py", "docs/template.md"]

                      db = Datastore("SQL Database")
                      db.OS = "CentOS"
                      db.controls.isHardened = False
                      db.inBoundary = server_db
                      db.type = DatastoreType.SQL
                      db.inScope = True
                      db.maxClassification = Classification.RESTRICTED
                      db.levels = [2]

                      secretDb = Datastore("Real Identity Database")
                      secretDb.OS = "CentOS"
                      secretDb.sourceFiles = ["pytm/pytm.py"]
                      secretDb.controls.isHardened = True
                      secretDb.inBoundary = server_db
                      secretDb.type = DatastoreType.SQL
                      secretDb.inScope = True
                      secretDb.storesPII = True
                      secretDb.maxClassification = Classification.TOP_SECRET

                      my_lambda = Lambda("AWS Lambda")
                      my_lambda.controls.hasAccessControl = True
                      my_lambda.inBoundary = vpc
                      my_lambda.levels = [1, 2]

                      token_user_identity = Data(
                          "Token verifying user identity", classification=Classification.SECRET
                      )
                      db_to_secretDb = Dataflow(db, secretDb, "Database verify real user identity")
                      db_to_secretDb.protocol = "RDA-TCP"
                      db_to_secretDb.dstPort = 40234
                      db_to_secretDb.data = token_user_identity
                      db_to_secretDb.note = "Verifying that the user is who they say they are."
                      db_to_secretDb.maxClassification = Classification.SECRET

                      comments_in_text = Data(
                          "Comments in HTML or Markdown", classification=Classification.PUBLIC
                      )
                      user_to_web = Dataflow(user, web, "User enters comments (*)")
                      user_to_web.protocol = "HTTP"
                      user_to_web.dstPort = 80
                      user_to_web.data = comments_in_text
                      user_to_web.note = "This is a simple web app\nthat stores and retrieves user comments."

                      query_insert = Data("Insert query with comments", classification=Classification.PUBLIC)
                      web_to_db = Dataflow(web, db, "Insert query with comments")
                      web_to_db.protocol = "MySQL"
                      web_to_db.dstPort = 3306
                      web_to_db.data = query_insert
                      web_to_db.note = (
                          "Web server inserts user comments\ninto it's SQL query and stores them in the DB."
                      )

                      comment_retrieved = Data(
                          "Web server retrieves comments from DB", classification=Classification.PUBLIC
                      )
                      db_to_web = Dataflow(db, web, "Retrieve comments")
                      db_to_web.protocol = "MySQL"
                      db_to_web.dstPort = 80
                      db_to_web.data = comment_retrieved
                      db_to_web.responseTo = web_to_db

                      comment_to_show = Data(
                          "Web server shows comments to the end user", classifcation=Classification.PUBLIC
                      )
                      web_to_user = Dataflow(web, user, "Show comments (*)")
                      web_to_user.protocol = "HTTP"
                      web_to_user.data = comment_to_show
                      web_to_user.responseTo = user_to_web

                      clear_op = Data("Serverless function clears DB", classification=Classification.PUBLIC)
                      my_lambda_to_db = Dataflow(my_lambda, db, "Serverless function periodically cleans DB")
                      my_lambda_to_db.protocol = "MySQL"
                      my_lambda_to_db.dstPort = 3306
                      my_lambda_to_db.data = clear_op

                      userIdToken = Data(
                          name="User ID Token",
                          description="Some unique token that represents the user real data in the secret database",
                          classification=Classification.TOP_SECRET,
                          traverses=[user_to_web, db_to_secretDb],
                          processedBy=[db, secretDb],
                      )

                      if __name__ == "__main__":
                          tm.process()

                    I'm using pytm: https://github.com/izar/pytm

                    do not start output.py with ```python

                    NOTE: Classification Levels are below. Do not use any other Taxonomy for Classification.
                      UNKNOWN = 0
                      PUBLIC = 1
                      RESTRICTED = 2
                      SENSITIVE = 3
                      SECRET = 4
                      TOP_SECRET = 5

                    IMPORTANT: Be thorough and extensive in building the output.py.

                    CRITICAL: elements have the following attributes:
                        OS
                        definesConnectionTimeout        default: False
                        description
                        handlesResources                default: False
                        implementsAuthenticationScheme  default: False
                        implementsNonce                 default: False
                        inBoundary
                        inScope                         Is the element in scope of the threat model, default: True
                        isAdmin                         default: False
                        isHardened                      default: False
                        name                            required
                        onAWS                           default: False

                      EXTREMELY IMPORTANT: Only send python code in the response, do not return anything else. Code should start with "from pytm import". """,
                "pytm",
            ),
        }
        task, topic = task_mapping.get(
            selected_task,
            ("A general task involving a general topic", "general"),
        )

        instruction = st.text_area("Request:", value="", height=150)

        button_container = st.container()

        with button_container:
            submit_button = st.columns([1])[0]  # Only keep the submit button

            with submit_button:
                if st.button("Submit"):
                    print("Submit button clicked")
                    st.session_state.clear()  # Clear session state
                    if instruction:
                        print("Processing message: {}...".format(instruction[:20]))
                        state = JarvisState(
                            instruction=instruction,
                            task=task,
                            topic=topic,
                        )
                        jarvis_flow = JarvisFlow(initial_state=state)
                        response = jarvis_flow.kickoff()
                        st.session_state["response"] = response[0]
                        st.session_state["response_type"] = response[1]
                    else:
                        print("No message provided by the user")

        if st.session_state["response"] and st.session_state["response_type"]:
            response_type = st.session_state["response_type"]
            response_blocks = st.session_state["response"]
            if response_type == "graphviz":
                st.markdown(response_blocks.get("diagram_text"))
                st.markdown(response_blocks.get("diagram_code"))
                print(response_blocks.get("diagram_code"))
                st.graphviz_chart(
                    response_blocks.get("diagram_code")
                    .replace("```graphviz", "")
                    .replace("```", ""),
                    use_container_width=True,
                )
            elif response_type == "pytm":
                st.markdown(response_blocks.get("diagram_text"))
                with st.expander("View Diagram Code"):
                    st.markdown(
                        "```python\n" + response_blocks.get("diagram_code") + "\n```"
                    )
                with open("pytm_output.py", "w") as file:
                    file.write(response_blocks.get("diagram_code"))

                command = "python pytm_output.py --dfd | dot -Tpng -o output.png"
                subprocess.run(command, shell=True, check=True)

                command_seq = "python3 pytm_output.py --seq | plantuml -tpng -pipe > seq_output.png"
                subprocess.run(command_seq, shell=True, check=True)
                col1, col2 = st.columns(2)

                command_report = "python pytm_output.py --report sample_report.txt | pandoc -f markdown > output-report.md"
                subprocess.run(command_report, shell=True, check=True)

                with col1:
                    st.image("output.png", use_container_width=True)
                with col2:
                    st.image("seq_output.png", use_container_width=True)

                st.markdown(open("output-report.md").read())
            elif response_type == "code":
                st.markdown(response_blocks.get("text"))
                with st.expander("View Code"):
                    st.markdown(
                        f"```{response_type}\n" + response_blocks.get("code") + "\n```"
                    )
            else:
                st.warning("Unsupported response type.")
        else:
            st.warning(
                "No valid response was generated. Please check your input or try again."
            )

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        st.error("An unexpected error occurred. Please try again later.")


if __name__ == "__main__":
    main()
