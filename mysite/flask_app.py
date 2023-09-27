# A very simple Flask Hello World app for you to get started with...
import signal
import subprocess
from flask import Flask, request, jsonify

INTERNAL_KEY = "password"
OPENAI_KEY = ""
WEBHOOK_URL = ""

app = Flask(__name__)   # This line should be moved up before any routes are defined

@app.route('/')
def hello_world():
    if OPENAI_KEY and WEBHOOK_URL and INTERNAL_KEY != "password":
        return 'The web server is working with OpenAI key and Webhook URL... '
    elif INTERNAL_KEY == "password":
        return 'The web server is working but password is missing... '
    elif OPENAI_KEY:
        return 'The web server is working but missing Webhook URL... '
    else:
        return 'The web server is working but missing OpenAI key... '

@app.route('/update-key/<passed_key>/<new_key>')
def update_key(passed_key, new_key):
    global INTERNAL_KEY
    if passed_key != INTERNAL_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    else:
        INTERNAL_KEY = new_key
        return 'The key is updated... '

@app.route('/update-password/<passed_key>/<new_key>')
def update_password(passed_key, new_key):
    global INTERNAL_KEY
    if passed_key != INTERNAL_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    else:
        INTERNAL_KEY = new_key
        return 'The key is updated... '

@app.route('/update-openai-key/<passed_key>/<openai_key>')
def update_openai_key(passed_key, openai_key):
    global OPENAI_KEY
    if passed_key != INTERNAL_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    else:
        OPENAI_KEY = openai_key
        return 'The OpenAI key is updated...'

@app.route('/update-webhook-url/<passed_key>/<path:webhook_url>')
def update_webhook_url(passed_key, webhook_url):
    global WEBHOOK_URL
    if passed_key != INTERNAL_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    else:
        WEBHOOK_URL = webhook_url
        return 'The Webhook URL is updated...'

subprocess_instance = None

@app.route('/webhook-endpoint/<passed_key>/', methods=['POST'])
def handle_webhook(passed_key):
    global subprocess_instance

    if passed_key != INTERNAL_KEY:
        return jsonify({"status": "error", "message": "Unauthorized"}), 403

    # Simple data validation if the POST has both URL and text.
    data = request.get_json()
    if not data.get("url") or not data.get("text"):
        return jsonify({"status": "error", "message": "Missing URL or text in the request."}), 400

    # Use subprocess to run your script
    try:
        subprocess_instance = subprocess.Popen(
            ["python3", "../auto-journal-club-server.py", "--openai_key", OPENAI_KEY, "--webhook_url", WEBHOOK_URL, "--url", data.get("url"), "--text", data.get("text")],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return jsonify({"status": "success", "message": "Script execution started!"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

def graceful_shutdown(signum, frame):
    """Handle shutdown gracefully by terminating the subprocess."""
    global subprocess_instance
    if subprocess_instance:
        subprocess_instance.terminate()
    exit(0)

signal.signal(signal.SIGINT, graceful_shutdown)  # Handle Ctrl+C
signal.signal(signal.SIGTERM, graceful_shutdown)  # Handle termination by other processes

if __name__ == '__main__':
    app.run(debug=True)
