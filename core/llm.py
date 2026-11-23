from langchain_groq import ChatGroq
import config


def get_llm():
    return ChatGroq(
        model=config.LLM_MODEL,
        api_key=config.LLM_API_KEY,
        temperature=0.2,  # low = fewer made-up answers
    )