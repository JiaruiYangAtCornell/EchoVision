from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from dotenv import load_dotenv
from vertexai.generative_models import GenerativeModel, Image
import vertexai
import os
import base64
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True,
     allow_headers=["Content-Type", "Authorization"])


def update_gcp_credentials(json_key:str):
    """Update GCP credentials using ada command"""
    try:
        if not os.path.isfile(json_key):
            raise FileNotFoundError(f"Credential file not found: {json_key}")

        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = json_key
        print(f"Credentials updated successfully: {json_key}")
        time.sleep(2)
        return True

    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        return False

def get_vertexai_client(region='us-central1') -> GenerativeModel:
    """Get Bedrock client with proper error handling"""
    vertexai.init(project='echo-version', location=region)
    vision_model = GenerativeModel("gemini-2.5-pro")

    return vision_model

@app.route('/analyze', methods=['POST'])
def analyze_image():
    try:
        # Validate request data
        if not request.json:
            return jsonify({'error': 'No JSON data provided'}), 400

        data = request.json

        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400

        # Extract base64 image data
        base64_image = data['image'].split(',')[1] if ',' in data['image'] else data['image']
        question = data.get('question', 'What do you see in this image?')
        with open("output_image.png", "wb") as f:
            f.write(base64.b64decode(base64_image))
        image = Image.load_from_file("output_image.png")
        print(f"Processing question: {question}")

        # Try to update AWS credentials (optional - may not be needed in all environments)
        if update_gcp_credentials('cred.json') == False:
            print("Warning: Could not update AWS credentials via ada command. Proceeding with existing credentials.")


        # Create vision_model client
        vision_model = get_vertexai_client()

        # Construct prompt
        prompt = f"Answer the following question from a blind/disability person in 4 to 5 sentences about the following image. Just answer the question directly without mentioning what you are or how you work: {question}"

        # Prepare GCP AI API
        response = vision_model.generate_content([prompt, image])

        # Parse response

        description = response.text
        print(f"Generated description: {description}")

        return jsonify({
            'description': description,
            'status': 'success'
        })


    except Exception as e:
        return jsonify({'error': f"Unexpected error: {str(e)}"}), 500

if __name__ == '__main__':
    print("Starting WorkSight Image Analyzer Server...")
    print("Server will run on http://localhost:5059")
    print("Health check available at http://localhost:5059/health")
    app.run(host='0.0.0.0', port=5059, debug=True)
