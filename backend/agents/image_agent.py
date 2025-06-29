from google.adk.agents import Agent
from vertexai.generative_models import GenerativeModel, Image
import base64
import os

os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "echo-version")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")

vision_model = GenerativeModel("gemini-2.5-pro")

def analyze_image_tool(input: dict) -> dict:
    base64_image = input.get("image", "")
    question = input.get("question", "What is in this image?")

    if not base64_image:
        return {"status": "error", "error_message": "Missing image data"}

    try:
        if ',' in base64_image:
            base64_image = base64_image.split(',')[1]
        image_data = base64.b64decode(base64_image)

        image_path = "/tmp/image.jpg"
        with open(image_path, "wb") as f:
            f.write(image_data)

        image = Image.load_from_file(image_path)
        prompt = (
            "Answer the following question from a blind person in 4–5 sentences. "
            "Do not explain what you are or how you work. Question: " + question
        )
        response = vision_model.generate_content([prompt, image])
        return {"status": "success", "description": response.text}

    except Exception as e:
        return {"status": "error", "error_message": str(e)}

echo_vision_agent = Agent(
    name="echo_vision_agent",
    model="gemini-2.5-pro",
    description="Answers image-based questions",
    tools=[analyze_image_tool]
)
