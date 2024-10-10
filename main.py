import os
import streamlit as st
import openai
import json
import logging
import anthropic
import graphviz
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

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
    }
    return expertise_statements.get(
        expertise_area,
        "You are an expert who values consistency and coherence. Only print what needs changing, dont print out everything.",
    )


def ask_gpt(question, INPUT_MODEL, selected_expertise):
    logging.info(
        f"Asking GPT: question={question[:20]}..., model={INPUT_MODEL}, selected_expertise={selected_expertise}"
    )
    expertise_statement = get_expertise_statement(selected_expertise)
    question_with_expertise = f"{expertise_statement}\n{question}\nOnly print what needs changing, dont print out everything.\nthink hard and deep.\n double check everything over and over again."

    try:
        if INPUT_MODEL == "claude-3-sonnet-20240229":
            response = ask_anthropic(question_with_expertise, INPUT_MODEL)
        else:
            response = ask_openai(question_with_expertise, INPUT_MODEL)
        return response
    except Exception as e:
        logging.error(f"Error occurred while asking model: {e}")
        return f"Error occurred: {str(e)}"


def ask_openai(question_with_expertise, INPUT_MODEL):
    chat_completion = openai.ChatCompletion.create(
        model="gpt-4o", messages=[{"role": "user", "content": question_with_expertise}]
    )
    return chat_completion.choices[0].message.content


def ask_anthropic(question_with_expertise, INPUT_MODEL):
    logging.info("Asking Anthropic using SDK")
    client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

    try:
        response = client.messages.create(
            model=INPUT_MODEL,
            max_tokens=4096,
            messages=[{"role": "user", "content": question_with_expertise}],
        )
        logging.debug(f"Anthropic SDK response: {response}")
        if response.content:
            return response.content[0].text
        else:
            raise Exception("No content in Anthropic response")
    except anthropic.APIError as e:
        logging.error(f"Anthropic API error: {str(e)}")
        raise Exception(f"Anthropic API error: {str(e)}")
    except Exception as e:
        logging.error(f"Unexpected error when calling Anthropic: {str(e)}")
        raise


# Load user credentials from yaml
with open("config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

# Create Streamlit Authenticator
authenticator = stauth.Authenticate(
    credentials=config["credentials"],
    cookie_name=config["cookie"]["name"],
    key=config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],  # corrected parameter name
)

# Start login
name, authentication_status, username = authenticator.login()

if authentication_status:
    selected_expertise = st.sidebar.radio(
        "Expertise Area", ("Python", "Javascript", "Flutter", "Diagram", "General")
    )
    logging.info(f"User selected expertise area: {selected_expertise}")

    model_options = {
        "Sonnet-3.5": "claude-3-sonnet-20240229",
        "GPT-4o": "gpt-4o",
        "GPT-o1": "o1-preview",
    }

    selected_model = st.sidebar.radio(
        "Select model", list(model_options.keys()), format_func=lambda k: k
    )
    INPUT_MODEL = model_options[selected_model]
    logging.info(f"User selected model: {INPUT_MODEL}")

    if not st.secrets.get("OPENAI_API_KEY"):
        logging.error("OpenAI API key not found.")
        st.error("OpenAI API key not found.")
        st.stop()

    if not st.secrets.get("ANTHROPIC_API_KEY"):
        logging.error("Anthropic API key not found.")
        st.error("Anthropic API key not found.")
        st.stop()

    logging.info("Setting OpenAI API key")
    openai.api_key = st.secrets["OPENAI_API_KEY"]

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
        else:
            st.write(f"**_zeus:** {st.session_state['response']}\n")

elif authentication_status == False:
    st.error("Username/password is incorrect")
elif authentication_status == None:
    st.warning("Please enter your username and password")
