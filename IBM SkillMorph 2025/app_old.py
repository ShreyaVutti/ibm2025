from flask import Flask, request, jsonify
from cloudant.client import Cloudant
from werkzeug.security import generate_password_hash
from flask_cors import CORS
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
CORS(app)  # Allow frontend to talk to backend

# Load credentials from environment
CLOUDANT_USERNAME = os.environ.get("CLOUDANT_USERNAME")
CLOUDANT_APIKEY = os.environ.get("CLOUDANT_APIKEY")
CLOUDANT_URL = os.environ.get("CLOUDANT_URL")

# Check for missing credentials
if not CLOUDANT_USERNAME or not CLOUDANT_APIKEY or not CLOUDANT_URL:
    raise EnvironmentError("Missing Cloudant credentials. Please set CLOUDANT_USERNAME, CLOUDANT_APIKEY, and CLOUDANT_URL.")

# Connect to Cloudant
client = Cloudant.iam(
    account_name=CLOUDANT_USERNAME,
    api_key=CLOUDANT_APIKEY,
    url=CLOUDANT_URL
)
client.connect()

# Create database if not exists
db = client.create_database("login_data", throw_on_exists=False)

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    hashed_pw = generate_password_hash(password)

    try:
        # Check if document already exists
        if email in db:
            return jsonify({"error": "User already exists"}), 409

        db.create_document({
            "_id": email,
            "password": hashed_pw
        })
        return jsonify({"message": "Login saved successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
