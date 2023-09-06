from flask import Flask, jsonify,  Response, send_file, request
import json
import Loan_Risk_Assessment_Notebook as lrs

app = Flask(__name__)


@app.route('/', methods=['GET'])
def hello():
    ascii_banner = "You have reached the endpoint for Loan Risk Assessment WebApp"
    return ascii_banner


@app.route('/fetch_score/', methods=['GET', 'POST'])
def fetch_trials():
    request_data = request.get_json(force=True)
    status = lrs.handle_request(request_data)
    return json.dumps(status)


if __name__ == '__main__':
    app.run(debug=True)