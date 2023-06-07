import vertexai
import os
from vertexai.preview.language_models import TextGenerationModel
from deep_translator import GoogleTranslator
from flask import Flask, jsonify, request

app = Flask(__name__)


def predict_large_language_model_sample(
        project_id: str,
        model_name: str,
        temperature: float,
        max_decode_steps: int,
        top_p: float,
        top_k: int,
        content: str,
        location: str = "us-central1",
        tuned_model_name: str = "",
):
    """Predict using a Large Language Model."""
    vertexai.init(project=project_id, location=location)
    model = TextGenerationModel.from_pretrained(model_name)
    if tuned_model_name:
        model = model.get_tuned_model(tuned_model_name)
    response = model.predict(
        content,
        temperature=temperature,
        max_output_tokens=max_decode_steps,
        top_k=top_k,
        top_p=top_p, )
    return response


@app.route("/")
def info():
    return jsonify({"info": "Use the /predict endpoint with the text parameter, you sanctimonius flesh vessel"})


@app.route("/predict", methods=['GET', 'POST'])
def predict():
    text = extract_text()
    if text is None:
        return jsonify({"result": "error", "message": "No text provided"}), 400
    return jsonify({"result": "success", "value": predict_text(text), "text": text})


def predict_text(text):
    result = predict_large_language_model_sample("hackathon23-latam-cumbiateam", "text-bison@001", 0.2, 256, 0.8, 40, '''Multi-choice problem: Define the category of the ticket?
Categories:
- Debt collection
- Mortgage
- Credit reporting
- Credit card
- Bank account
- Bank service
- Student loan
- Credit reporting
- Credit repair
- Consumer Loan
- Checking account
- Savings account
- Payday loan
- Money transfers
- Prepaid card
- Undefined

Ticket: {0} 
Category:
'''.format(text), "us-central1")
    return result


def extract_text():
    args = request.args
    text: str | None = args.get("text")
    if text is None and "text" in request.form:
        text = request.form["text"]
    if text is None:
        text = request.json["text"]
    return text


@app.route("/predecir", methods=['GET', 'POST'])
def predecir():
    translator = GoogleTranslator(source='es', target='en')
    text_spanish = extract_text()
    if text_spanish is None:
        return jsonify({"result": "error", "message": "No text provided"}), 400
    text_english = translator.translate(text_spanish)
    result = predict_text(text_english)
    translator = GoogleTranslator(source='en', target='es')
    if result.text:
        result.text = translator.translate(result.text)
    return jsonify({"result": "success", "value": result, "text": text_spanish, "translated": text_english})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
