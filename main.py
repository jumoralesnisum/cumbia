import vertexai
import os
from vertexai.preview.language_models import TextGenerationModel
from deep_translator import GoogleTranslator
from flask import Flask, jsonify, request
from google.cloud import aiplatform
from google.cloud.aiplatform.gapic.schema import predict as gpredict
from google.protobuf import json_format
from google.protobuf.struct_pb2 import Value

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
    (text, index) = extract_text()

    if text is None:
        return jsonify({"result": "error", "message": "No text provided"}), 400
    print("text is {} index is {}".format(text, index))
    result = None
    if index == 2:
        print("TWO")
        result = predict_with_small_model(text)
    elif index == 1:
        print("ONE")
        result = predict_text(text)
    return jsonify({"result": "success", "value": result, "text": text})


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
    index: int | None = args.get("index")
    if text is None and "text" in request.form:
        text = request.form["text"]
        if "index" in request.form:
            index = request.form["index"]
    if text is None and "text" in request.json:
        text = request.json["text"]
        if "index" in request.json:
            index = request.json["index"]
    if text is not None and len(text) == 0:
        text = None
    if index is None:
        index = 1
    return text, int(index)


@app.route("/predecir", methods=['GET', 'POST'])
def predecir():
    text_spanish, index = extract_text()
    if text_spanish is None:
        return jsonify({"result": "error", "message": "No text provided"}), 400
    result = None
    if index == 2:
        result = predict_with_small_model(text_spanish)
        text_english = ""
    elif index == 1:
        translator = GoogleTranslator(source='es', target='en')
        text_english = translator.translate(text_spanish)
        result = predict_text(text_english)
        translator = GoogleTranslator(source='en', target='es')
        if result.text:
            result.text = translator.translate(result.text)
    return jsonify({"result": "success", "value": result, "text": text_spanish, "translated": text_english})


@app.route("/predict2", methods=['GET', 'POST'])
def predict2():
    text,index = extract_text()
    if text is None:
        return jsonify({"result": "error", "message": "No text provided"}), 400
    return jsonify({"result": "success", "value": predict_with_small_model(text), "text": text})


def predict_with_small_model(text):
    api_endpoint = "us-central1-aiplatform.googleapis.com"
    project = "630804675018"  # "hackathon23-latam-cumbiateam"
    location = "us-central1"
    endpoint_id = "8376585355746344960"
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.PredictionServiceClient(client_options=client_options)
    instance = gpredict.instance.TextClassificationPredictionInstance(
        content=text,
    ).to_value()
    instances = [instance]
    parameters_dict = {}
    parameters = json_format.ParseDict(parameters_dict, Value())
    endpoint = client.endpoint_path(
        project=project, location=location, endpoint=endpoint_id
    )
    response = client.predict(
        endpoint=endpoint, instances=instances, parameters=parameters
    )
    dict_response = type(response).to_dict(response)
    confidences = dict_response.get('predictions')[0].get('confidences')
    position = confidences.index(max(confidences))
    text = dict_response.get('predictions')[0].get('displayNames')[position]
    dict_response['text'] = text
    return dict_response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
