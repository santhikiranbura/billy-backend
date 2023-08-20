from flask import Flask, request, jsonify
from flask_cors import CORS
import billy
import json

app = Flask(__name__)

CORS(app)


@app.route("/", methods=["POST"])
def main():
    req_data = request.get_json(force=True)
    query = req_data["query"]
    data = req_data["data"]
    name = req_data["name"]
    event = billy.Event(name, query, data)
    return jsonify({"name": event.name, "data": event.data})


# podman build -t billy:1.0.0 .
# podman tag billy:1.0.0 santhi0802/billy:1.0.0


@app.route("/", methods=["GET"])
def check():
    return "Connected Successfully"


if __name__ == "__main__":
    from waitress import serve

    print("Connected to Server")
    serve(app, host="0.0.0.0", port=8082)
