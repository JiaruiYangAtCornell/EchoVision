from flask import jsonify

# import agent
from agents.image_agent import echo_vision_agent
from agents.text_agent import text_agent

PROJECT_ID = "echo-version"
REGION = "us-central1"

vertexai.init(project=PROJECT_ID, location=REGION)
vision_model = GenerativeModel("gemini-2.5-pro")
# analyze_image 是你的 function entry point
def analyze_image(request):
    
    if request.method == 'OPTIONS':
        return '', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({'error': 'Missing JSON payload'}), 400, headers

        result = echo_vision_agent.run_tool("analyze_image_tool", payload)
        return jsonify({
            'description': result.get('description', ''),
            'status': 'success'
        }), 200, headers

    except Exception as e:
        return jsonify({'error': str(e)}), 500, headers


def analyze_text(request):
    if request.method == 'OPTIONS':
        return '', 204, {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
        }

    headers = {'Access-Control-Allow-Origin': '*'}

    try:
        payload = request.get_json(silent=True)
        if not payload:
            return jsonify({'error': 'Missing JSON payload'}), 400, headers

        result = text_agent.run_tool("summarize_text", payload)
        return jsonify({
            'description': result.get('description', ''),
            'status': 'success'
        }), 200, headers

    except Exception as e:
        return jsonify({'error': str(e)}), 500, headers
