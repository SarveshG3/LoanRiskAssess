import requests
import json
import urllib3
import threading
import pandas as pd
from pandas import json_normalize
import ast
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import MinMaxScaler
import pickle
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

loaded_model = None

def prepare_data(data):
    data
    df = pd.json_normalize(data)
    #df.drop('appID', axis=1, inplace=True)
    df.drop('serial', axis=1, inplace=True)
    df.drop('name', axis=1, inplace=True)
    df.drop('address', axis=1, inplace=True)
    df.drop('SSN', axis=1, inplace=True)
    df.drop('Score', axis=1, inplace=True)
    df.drop('phone', axis=1, inplace=True)
    df.drop('Existing Loan?',axis=1,inplace=True)
    df.drop('Existing Loan Outstanding Amount ', axis=1, inplace=True)
    df.drop('loan_int_rate',axis=1,inplace=True)
    df.drop('loan_grade', axis=1, inplace=True)
    df.drop('loan_status', axis=1, inplace=True)
    return df

def predict(row):
    print('----------row----------')
    print(row)
    df = row.values.reshape(1, -1)
    print('----------df----------')
    print(df)
    print("Loaded Model:")
    print(loaded_model)
    prediction = loaded_model.predict_proba(df)
    print(prediction)
    pred_value = prediction.item(0, 1) * 100
    old_min, old_max, new_min, new_max = [0, 100, 400, 1000]
    scaled_pred = ((pred_value - old_min) / (old_max - old_min)) * (new_max - new_min) + new_min
    return scaled_pred

def send_to_powerApps(score_data):
    url = 'INSERT URL HERE'
    headers = {'Content-Type': 'application/json',
               'api-key': 'API KEY GOES HERE'}
    try:
        response = requests.post(url, headers=headers, data=score_data, verify=True)
        print("POST response code: " + str(response.status_code))
        if response.status_code == 200:
            ssh_keys = json.loads(response.content.decode('utf-8'))
            return ssh_keys
        else:
            print('[?] Unexpected Error: [HTTP {0}]: Content: {1}'.format(response.status_code, response.content))
    except requests.exceptions.RequestException as e:
        print(e)

def prepare_send_result(json_data):
    global loaded_model
    out={1:"Reject", 0:"Approve", 2: "Underwriting"}
    data = json.loads(json_data)
    print('--------------------------Request--------------------------')
    print(data)
    model_df = prepare_data(data)
    with open(r"/content/sample_data/best_pipeline.pkl", 'rb') as file:
        loaded_model = joblib.load(file)
    #print(model_df)
    model_df['prediction'] = loaded_model.predict(model_df)
    model_df['loan_status'] = out[model_df['prediction'][0]]
    #print(model_df['riskScore'])
    model_df.reset_index(inplace=True)
    returnString = model_df.to_json(orient='records')
    #relevant_results = model_df[['appID', 'loan_status']]
    #returnString = relevant_results.to_json(orient='records')
    #res = send_to_powerApps(json.dumps({'appID': model_df['appID'], 'score': returnString}))
    #print(json.dumps(res))
    return returnString

def handle_request(req_data):
    #prepare_send_result(req_data)
    threading.Thread(target=prepare_send_result, args=(req_data), name="predict_result",
                    daemon=True).start()
    return "Data received successfully"

if __name__ == '__main__':
    #print('Main Started...')
    response = prepare_send_result(input_json)
    print('--------------------------Response--------------------------')
    print(response)

