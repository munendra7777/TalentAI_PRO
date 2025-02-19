def get_model_options():
    return {
        "LLM": ["GPT-3", "GPT-4", "BERT", "T5"],
        "Embedding": ["Sentence-BERT", "Universal Sentence Encoder", "OpenAI Embeddings"]
    }

def render_model_selection():
    model_options = get_model_options()
    
    selected_llm = st.selectbox("Select LLM Model", model_options["LLM"])
    selected_embedding = st.selectbox("Select Embedding Model", model_options["Embedding"])
    
    return selected_llm, selected_embedding