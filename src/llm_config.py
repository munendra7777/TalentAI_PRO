class LLMConfig:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = "gemini/gemini-1.5-flash-8b"
        self.temperature = 0.5

def get_llm_config(api_key):
    return LLMConfig(api_key)
