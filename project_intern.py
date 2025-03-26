import os
import webbrowser
import faiss
import numpy as np
from flask import Flask, request, jsonify, render_template
from sentence_transformers import SentenceTransformer


app = Flask(__name__)


model = SentenceTransformer("all-MiniLM-L6-v2")

def open_chrome():
    webbrowser.open("https://www.google.com")

def open_calculator():
    os.system("calc")

def get_cpu_usage():
    output =  os.popen("wmic cpu get loadpercentage").read()
    return output.strip().split("\n")[-1].strip()

function_descriptions = {
    "open_chrome": "Launch Google Chrome browser",
    "open_calculator": "Open calculator application",
    "get_cpu_usage": "Retrieve CPU usage information"
}

dimension = model.get_sentence_embedding_dimension()
index = faiss.IndexFlatL2(dimension)
function_names = list(function_descriptions.keys())
function_embeddings = model.encode(list(function_descriptions.values()))
index.add(np.array(function_embeddings))


@app.route("/execute", methods=["POST"])
def execute_function():
    if not request.is_json:
        return jsonify({"error": "Invalid content type. Use 'application/json'."}), 400
    
    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing 'prompt' field in request body."}), 400
    
    prompt = data["prompt"]

    query_embedding = model.encode([prompt])
    _, idx = index.search(np.array(query_embedding), 1)
    function_name = function_names[idx[0][0]]

    generated_code = f"""
from __main__ import {function_name}

def main():
    try:
        result = {function_name}()
        print("Function executed successfully.")
        return result
    except Exception as e:
        print(f"Error executing function: {{e}}")

if __name__ == "__main__":
    main()
    """

    try:
        result = globals()[function_name]()
        return jsonify({
            "status": "success",
            "function": function_name,
            "executed": True,
            "code": generated_code.strip(),
            "result": result if result else "Executed successfully"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "function": function_name,
            "executed": False,
            "message": "Function execution failed",
            "error": str(e)
        }), 500

if __name__ == "__main__":
    app.run(port=8000, debug=True)
