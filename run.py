from flask import Flask, request, jsonify
import billy
import json

app = Flask(__name__)


@app.route("/", methods=["POST"])
def main():
    req_data = request.get_json(force=True)
    print(req_data)
    query = req_data["query"]
    data = req_data["data"]
    name = req_data["name"]
    event = billy.Event(name, query, data)
    return jsonify({"name": event.name, "data": event.data})


@app.route("/", methods=["GET"])
def check():
    return "Connected Successfully"


if __name__ == "__main__":
    from waitress import serve

    print("Connected to Server")
    serve(app, host="0.0.0.0", port=8080)
