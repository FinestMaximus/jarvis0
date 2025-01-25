import os
import streamlit as st
import json
import logging
import graphviz
import yaml
from yaml.loader import SafeLoader
from openai import OpenAI


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

# Streamlit styling
st.markdown(
    """
    <style>
        body {
            background-color: #333333;
            color: #00FF00;
        }
        .stTextArea textarea, .stButton>button, .stSidebar,
        .stSidebar>div {
            background-color: #333333;
            color: #00FF00;
        }
        .stButton>button:hover {
            background-color: #444444;
        }
        .stAlert, .stMarkdown {
            background-color: #333333;
            color: #00FF00;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def get_expertise_statement(expertise_area):
    logging.info(f"Getting expertise statement for {expertise_area}")
    expertise_statements = {
        "Python": "As a Python development expert, you engage in profound analysis and meticulous double-checking to guarantee the utmost consistency and coherence in your solutions, continuously solving complex problems with precision.",
        "Javascript": "As a Node.js development expert, you apply thorough and reflective analysis, coupled with rigorous double-checking, to deliver highly consistent and coherent solutions, adeptly solving complex issues.",
        "Flutter": "As a Flutter/Dart development expert, you combine intensive analytical thinking and careful double-checking to achieve optimal consistency and coherence, expertly addressing challenging problems.",
        "Diagram": "You excel at generating precise and coherent graphviz gradient cluster diagrams for code and process representations, ensuring clarity and accuracy. Return only the graphviz script without additional text or formatting. Do not start the response with ```. I want an Advanced fancy Diagram. I want large text fonts, and readable graphs. The graph must read from top to bottom. Ensure I can see Start at the top, End at the bottom and all conditions related to the different processes (each process in its own cluster).",
        "General": "As an expert across various domains, you employ deep analytical thinking and thorough double-checking to ensure exceptional consistency and coherence, resolving intricate challenges with remarkable problem-solving skills.",
        "PyTM": """You are an expert in PyTM, a Python-based tool for creating and managing technical documents. You are able to generate PyTM code and diagrams that are both accurate and visually appealing. You are also able to generate PyTM code that is both accurate and visually appealing. You are also able to generate PyTM code that is both accurate and visually appealing. you're a pytm threat modeling expert, who only sends python code back (no other output). Based on current context // more prompting here..
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
    }  # Context as a system message

    return expertise_statements.get(
        expertise_area,
        "You are an expert who values consistency and coherence. Only print what needs changing, dont print out everything.",
    )


def ask_gpt(question, INPUT_MODEL, selected_expertise, add_prompt, system_prompt):
    logging.info(
        f"Asking GPT: question={question[:20]}..., model={INPUT_MODEL}, selected_expertise={selected_expertise}"
    )
    expertise_statement = get_expertise_statement(selected_expertise)
    prompt_addition = (
        "\nthink hard and deep.\n double check everything over and over again."
        if not add_prompt
        else "\nOnly print what needs changing, dont print out everything. Be brief. \nthink hard and deep.\n double check everything over and over again."
    )
    question_with_expertise = (
        f"{expertise_statement}{system_prompt}{prompt_addition}\n{question}"
    )

    try:
        return ask_openai(question_with_expertise, INPUT_MODEL)
    except Exception as e:
        logging.error(f"Error occurred while asking model: {e}")
        return f"Error occurred: {str(e)}"


def ask_openai(question_with_expertise, INPUT_MODEL):
    chat_completion = client.chat.completions.create(
        model=INPUT_MODEL,
        messages=[{"role": "user", "content": question_with_expertise}],
    )
    return chat_completion.choices[0].message.content


# Load user credentials from yaml
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

selected_expertise = st.sidebar.radio(
    "Expertise Area",
    ("Python", "Javascript", "Flutter", "Diagram", "General", "PyTM"),
)
logging.info(f"User selected expertise area: {selected_expertise}")

model_options = {
    "GPT-4o-mini": "gpt-4o-mini",
    "GPT-4o": "gpt-4o",
}

selected_model = st.sidebar.radio(
    "Select model", list(model_options.keys()), format_func=lambda k: k
)
INPUT_MODEL = model_options[selected_model]
logging.info(f"User selected model: {INPUT_MODEL}")

add_prompt = st.sidebar.checkbox("Be Brief")

system_prompt = st.sidebar.text_area("System Prompt", height=100)

if not st.secrets.get("OPENAI_API_KEY"):
    logging.error("OpenAI API key not found.")
    st.error("OpenAI API key not found.")
    st.stop()

logging.info("Setting OpenAI API key")

# Instantiate the OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Initialize or reset history
if "history" not in st.session_state:
    st.session_state["history"] = []
    st.session_state["reset_history"] = False

if st.session_state["reset_history"]:
    st.session_state["history"] = []
    st.session_state["reset_history"] = False

message = st.text_area("Message:", value="", height=150)

# Container for buttons to ensure they are properly laid out
button_container = st.container()

with button_container:
    submit_button, clear_history_button = st.columns([1, 5])

    with submit_button:
        if st.button("Submit"):
            logging.info("Submit button clicked")
            if message:
                logging.info(f"Processing message: {message[:20]}...")
                st.session_state["history"].append(message)
                response = ask_gpt(
                    message,
                    INPUT_MODEL,
                    selected_expertise,
                    add_prompt,
                    system_prompt,
                )
                st.session_state["response"] = response
            else:
                logging.info("No message provided by the user")

    with clear_history_button:
        if st.button("Clear History"):
            logging.info("Clear History button clicked")
            st.session_state["reset_history"] = True
            st.session_state["history"] = []
            st.session_state["response"] = ""

# Display the response after processing
if "response" in st.session_state and st.session_state["response"]:
    if selected_expertise == "Diagram":
        try:
            graphviz_code = st.session_state["response"].strip("```").strip()
            st.graphviz_chart(graphviz_code)
        except Exception as e:
            logging.error(f"Failed to render Graphviz diagram: {e}")
            st.error(f"Error occurred while rendering diagram: {e}")
    elif selected_expertise == "PyTM":
        try:
            logging.info("Generating PyTM diagram...")
            # Define the path for the output Python file
            pytm_output = "output.py"
            print(pytm_output)

            with open(pytm_output, "w") as f:
                f.write(st.session_state["response"])

            # Run the output Python file to generate the diagram
            command = f"python {pytm_output} --dfd | dot -Tpng -o output.png"
            os.system(command)
            logging.info(
                "PyTM diagram generated successfully and saved as output.png using command: {command}"
            )

            # Display the generated PNG diagram
            st.image(
                "output.png", caption="Generated PNG diagram", use_container_width=True
            )
        except Exception as e:
            logging.error(f"Failed to generate PNG: {e}")
            st.error(f"Error occurred while generating PNG: {e}")
    else:
        st.write(f"**_zeus:** {st.session_state['response']}\n")
