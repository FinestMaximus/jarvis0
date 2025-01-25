#!/usr/bin/env python
import logging
import os
import streamlit as st
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
import yaml
from crews.jarvis_crew.jarvis_crew import JarvisCrew
import subprocess  # Added for secure subprocess handling

# Add logging configuration


class JarvisState(BaseModel):
    data: str = ""


class JarvisFlow(Flow[JarvisState]):
    def __init__(self, initial_state: JarvisState):
        super().__init__()
        self._state = initial_state

    @start()
    def generate_data(self):
        print(f"Entering generate_data method with inputs provided: {self._state.data}")

    @listen(generate_data)
    def generate_python_code(self):
        try:
            print("Initializing JarvisCrew...")
            inputs = {"data": self._state.data}

            results = JarvisCrew().python_developement_team().kickoff(inputs=inputs)

            # print(f"Results: {results.pydantic}")

            self.python_code = results.pydantic.model_dump().get("python_code", "")
            print(f"Generated Python code: {self.python_code}")

            return self.python_code

        except Exception as e:
            print(f"Error in JarvisCrew execution: {e}")
            self.python_code = ""


def plot():
    jarvis_flow = JarvisFlow(JarvisState())
    jarvis_flow.plot()


def main() -> None:
    try:
        print("Checking if config.yaml exists")
        if not os.path.exists("src\jarvis\main.py"):
            st.error("Configuration file 'config.yaml' not found.")
            print("Configuration file 'config.yaml' not found.")
            st.stop()

        print("Loading user credentials from config.yaml")
        with open("config.yaml") as file:
            config = yaml.load(file, Loader=yaml.SafeLoader)
            print(f"Config loaded: {config}")

        selected_expertise = st.sidebar.radio(
            "Expertise Area",
            ("Python", "Javascript", "Flutter", "Diagram", "General", "PyTM"),
        )
        print("User selected expertise area: {}".format(selected_expertise))

        if not st.secrets.get("OPENAI_API_KEY"):
            st.error(
                "OpenAI API key is missing. Please check your secrets configuration."
            )
            print("OpenAI API key is missing.")
            st.stop()

        print("Setting OpenAI API key")

        data = st.text_area("Request:", value="", height=150)
        print("User input data: {}".format(data))

        print("Creating button container for layout")
        button_container = st.container()

        with button_container:
            submit_button = st.columns([1])[0]  # Only keep the submit button

            with submit_button:
                if st.button("Submit"):
                    print("Submit button clicked")
                    if data:
                        print("Processing message: {}...".format(data[:20]))
                        state = JarvisState(data=data)
                        jarvis_flow = JarvisFlow(initial_state=state)
                        response = jarvis_flow.kickoff()
                        print(f"Response before setting session state: {response}")
                        st.session_state["response"] = response
                        print(
                            f"Updated session state with response: {st.session_state.get('response')}"
                        )
                    else:
                        print("No message provided by the user")

        if "response" in st.session_state and st.session_state["response"]:
            print("Displaying response after processing")
            if selected_expertise == "Diagram":
                try:
                    graphviz_code = st.session_state["response"].strip("```").strip()
                    print(f"Graphviz code to render: {graphviz_code}")
                    st.graphviz_chart(graphviz_code)
                    print("Graphviz diagram rendered successfully")
                except Exception as e:
                    print("Failed to render Graphviz diagram: {}".format(e))
                    st.error(f"Error occurred while rendering diagram: {e}")
            elif selected_expertise == "PyTM":
                try:
                    print("Generating PyTM diagram...")
                    pytm_output = "output.py"
                    with open(pytm_output, "w") as f:
                        f.write(st.session_state["response"])
                        print(f"PyTM output written to: {pytm_output}")

                    command = ["python", pytm_output, "--dfd"]
                    print(f"Running command: {command}")
                    subprocess.run(command, check=True)
                    subprocess.run(
                        ["dot", "-Tpng", "-o", "output.png"],
                        input="output.py",
                        text=True,
                        check=True,
                    )
                    print("PyTM diagram generated successfully")

                    st.image(
                        "output.png",
                        caption="Generated PNG diagram",
                        use_container_width=True,
                    )
                except subprocess.CalledProcessError as e:
                    print("Subprocess failed: {}".format(e))
                    st.error("Failed to generate diagram. Please check your input.")
            else:
                print(f"Displaying response: {st.session_state['response']}")
                st.write(f"**_zeus:** {st.session_state['response']}\n")
        else:
            st.warning(
                "No valid response was generated. Please check your input or try again."
            )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        st.error("An unexpected error occurred. Please try again later.")


if __name__ == "__main__":
    main()
