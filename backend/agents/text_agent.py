from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel

text_model = GenerativeModel("gemini-1.5-pro")

def summarize_text(input: dict) -> dict:
    text = input.get("text", "")
    if not text:
        return {"status": "error", "error_message": "Missing text"}
    prompt = "Summarize the following:\n" + text
    response = text_model.generate_content(prompt)
    return {"status": "success", "summary": response.text}

text_agent = Agent(
    name="text_summarizer_agent",
    model="gemini-1.5-pro",
    description="Summarize user text",
    tools=[summarize_text]
)
