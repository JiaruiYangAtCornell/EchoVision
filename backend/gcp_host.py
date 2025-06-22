import base64
import json
from flask import jsonify
from vertexai.generative_models import GenerativeModel, Image
import vertexai

PROJECT_ID = "echo-version"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)
vision_model = GenerativeModel("gemini-2.5-pro")

def analyze_image(request):
    # ✅ Step 1: Handle CORS preflight
    if request.method == 'OPTIONS':
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }
        return ('', 204, headers)

    # ✅ Step 2: Handle actual POST request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    try:
        request_json = request.get_json(silent=True)

        if not request_json or 'image' not in request_json:
            return (jsonify({'error': 'Missing image data'}), 400, headers)

        base64_image = request_json['image']
        question = request_json.get('question', 'What is in this image?')

        # Clean base64
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
        description = response.text

        return (jsonify({
            'description': description,
            'status': 'success'
        }), 200, headers)

    except Exception as e:
        print("❌ Error:", str(e))
        return (jsonify({'error': f'Unexpected error: {str(e)}'}), 500, headers)
