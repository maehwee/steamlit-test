import streamlit as st
from openai import OpenAI

import io

#--- Model Usage ---
# #OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
HF_API_KEY = st.secrets["HF_API_KEY"]

HF_PROVIDER = "huggingface"
HF_CUSTOM_PROVIDER = "huggingface-custom"
FAKE_PROVIDER = "fake"

MAX_TOKENS = 500

MODEL_OPTIONS = {
    # Hugging Face models
    "llama-3.2-1B-Instruct": {"provider": HF_PROVIDER, "id": "meta-llama/Llama-3.2-1B-Instruct"},
    "llama-3.2-3B-Instruct": {"provider": HF_PROVIDER, "id": "meta-llama/Llama-3.2-3B-Instruct"},
    "phi-3.5-mini-instruct": {"provider": HF_PROVIDER, "id": "microsoft/Phi-3.5-mini-instruct"},
    "Qwen/QwQ-32B-Preview": {"provider": HF_PROVIDER, "id": "Qwen/QwQ-32B-Preview"},

    # # OpenAI models
    # "gpt-3.5-turbo": {"provider": OPENAI_PROVIDER, "id": "gpt-3.5-turbo"},
    # "gpt-4o": {"provider": OPENAI_PROVIDER, "id": "gpt-4o"},
    # "gpt-4o-mini": {"provider": OPENAI_PROVIDER, "id": "gpt-4o-mini"},

    # Special models
    "fake-model": {"provider": FAKE_PROVIDER, "id": "fake"},
    "other hugging face model": {"provider": HF_CUSTOM_PROVIDER, "id": "replaced-by-write-in"},
}


def get_provider_callable(model_key):
    """
    Get a callable for the provider of the selected model
    """
    chosen_model = MODEL_OPTIONS[model_key]
    provider = chosen_model["provider"]

    if provider == FAKE_PROVIDER:
        return get_fake_response
    
    if provider == HF_PROVIDER:
        return get_hf_response
    
    if provider == HF_CUSTOM_PROVIDER:
        return get_hf_response
    
    return None


def get_response(model_key, messages, custom_model_id=None):
    """
    Get a response from the model selected in the sidebar
    """
    provider = get_provider_callable(model_key)

    if provider is None:
        return io.StringIO("No model was queried")
    
    model_id = MODEL_OPTIONS[model_key]["id"]

    if custom_model_id:
        model_id = custom_model_id 
    
    return provider(model_id, messages)    


def format_hf_endpoint(model_id):
    """
    Format the endpoint for a Hugging Face model from its id

    e.g. for google/gemma-2-2b-it it will be:
    https://api-inference.huggingface.co/models/google/gemma-2-2b-it/v1/chat/completions
    """
    return f"https://api-inference.huggingface.co/models/{model_id}/v1/"


def get_hf_response(model_id, messages):
    """
    Get a streamed response from Hugging Face
    """
    endpoint = format_hf_endpoint(model_id)

    # # init the client but point it to HF's TGI inference endpoint
    client = OpenAI(
        base_url=endpoint,
        api_key=HF_API_KEY,
    )

    chat_completion = client.chat.completions.create(
        model="tgi",
        messages=format_message_list(messages),
        stream=True,
        max_tokens=MAX_TOKENS,
    )

    return chat_completion

def is_custom_model(model_key):
    """
    Check if the model is a custom model
    """
    return MODEL_OPTIONS[model_key]["provider"] == HF_CUSTOM_PROVIDER


def format_message_list(messages):
    """
    Format the messages to pass to an LLM
    """
    message_list = [{"role": m["role"], "content": m["content"]} for m in messages]
    return message_list


def get_fake_response(unused_model_id, unused_messages):
    """
    Fake a streamed response
    """
    responses = [
        "Hello there! How can I help you today?",
        "Hi human! Is there anything I can help with?",
        "Do you need help?",
    ]
    
    return io.StringIO(random.choice(responses))


#--- UI Parts ---
def model_options_ui():
    with st.sidebar:
        st.radio("Model", options=MODEL_OPTIONS, index=0, key="selected_model")

        # Add textbox for custom model ID if one of those optiosn was chosen above
        chosen_model = get_chosen_model()

        if is_custom_model(chosen_model):
            st.text_input("Custom model ID", key="custom_model_id", help="HF model ide.g. microsoft/Phi-3.5-mini-instruct")
 
def get_chosen_model():
    return st.session_state["selected_model"]


#--- Main Page ---
st.markdown("# Multiple Choice Quiz")
st.markdown("#### Create a multiple choice quiz based on a grade level and topic")

# Create a form
with st.form('create_quiz'):
    # Create two dropdown menus
    grade_level = st.selectbox("Grade level:", 
                                options = ["Pre-K", "Kindergarten", "1st grade", "2nd grade", "3rd grade", "4th grade", "5th grade", "6th grade", "7th grade", "8th grade", "9th grade", "10th grade", "11th grade", "12th grade"],
                                index = 13)
    n_questions = st.selectbox("Number of questions:", 
                                options = ["3", "5", "10"],
                                index = 0)

    # Create a textbox
    quiz_topic = st.text_area("Quiz topic:", 
                                placeholder="US History", 
                                height=150, 
                                )
    
    quiz_prompt = f'''I am a teacher. Please create a multiple choice quiz about {quiz_topic} for {grade_level} students.
                    The quiz should have {n_questions} questions, and each question should have 4 possible answers. 
                    Please include a Title at the top of the quiz and an Answer Key at the end of the quiz.
                    '''
    submit = st.form_submit_button('Create Quiz', type="primary", use_container_width=True)

if submit:
    if (quiz_topic == ""):
        st.error("Please enter a topic")
    else:
        with st.spinner("Generating quiz..."):
            # Generate the quiz
            # generate_quiz(grade_level, n_questions, quiz_topic)
            st.success("Quiz generated!")
            st.markdown(quiz_prompt)





# # Generate quiz
# if st.button("Generate Quiz", type="primary", use_container_width=True):
#     if (quiz_topic == ""):
#         st.error("Please enter a topic")
#     else:
#         with st.spinner("Generating quiz..."):
#             # Generate the quiz
#             # generate_quiz(grade_level, n_questions, quiz_topic)
#             st.success("Quiz generated!")

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

model_options_ui()



# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What's up?"):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        chosen_model = get_chosen_model()
        messages = st.session_state.messages
        custom_model_id = None

        if is_custom_model(chosen_model):
            custom_model_id = st.session_state["custom_model_id"]  

        llm_response = get_response(model_key=chosen_model, messages=messages, custom_model_id=custom_model_id)
        response = st.write_stream(llm_response)

    st.session_state.messages.append({"role": "assistant", "content": response})
