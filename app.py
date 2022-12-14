from flask import Flask, request
import requests # used to make request to mpesa api
from requests.auth import HTTPBasicAuth # for authentification purposes
import json
from datetime import datetime
import base64

app = Flask(__name__)



@app.route('/')
def home():
    return 'Hello World!'

@app.route('/access_token')
def get_access_token():
    global consumer_key    
    global consumer_secret

    #base_url = '' # used for domain names or any other ip address one may require to use
    consumer_key = 'wT7uN60NNAiJA9KyXb7AepQAOkaRcotC'
    consumer_secret = 'cwVyibjc98Cfh1wM'
   

    consumer_key = consumer_key # gets consumer keys above 
    consumer_secret = consumer_secret # get the consumer secret above
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials' # safaricom url or endpoint

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret)) # darajaapi endpoint and authentification(requires consumer_key and consumer_secret) which enables user to have access to the access_token
    data = r.json() # convert data to json 
    return data['access_token'] # returning the access token



@app.route('/register')
def register_urls():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl' # 
    access_token = _access_token() # get the access token from the function _access_token 
    my_endpoint = "c2b/" #This is used to access both C2B confirmation and C2B validation
    headers = { "Authorization": "Bearer %s" % access_token }
    r_data = {
        "ShortCode": "600247",
        "ResponseType": "Completed",
        "ConfirmationURL": my_endpoint + 'con', # This gets the base_url + C2B confirmation from 'c2b/con'
        "ValidationURL": my_endpoint + 'val'  # This gets the base_url + C2B validation from 'c2b/val'
    }

    response = requests.post(endpoint, json = r_data, headers = headers)
    return response.json()


@app.route('/simulate')
def test_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate'
    access_token = _access_token()
    headers = { "Authorization": "Bearer %s" % access_token }

    data_s = {
        "Amount": 100,
        "ShortCode": "600247",
        "BillRefNumber": "test",
        "CommandID": "CustomerPayBillOnline",
        "Msisdn": "254741151005"
    }

    res = requests.post(endpoint, json= data_s, headers = headers)
    return res.json()

@app.route('/b2c')
def make_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest'
    access_token = _access_token()
    headers = { "Authorization": "Bearer %s" % access_token }
    my_endpoint = "/b2c/"

    data = {
        "InitiatorName": "apitest342",
        "SecurityCredential": "SQFrXJpsdlADCsa986yt5KIVhkskagK+1UGBnfSu4Gp26eFRLM2eyNZeNvsqQhY9yHfNECES3xyxOWK/mG57Xsiw9skCI9egn5RvrzHOaijfe3VxVjA7S0+YYluzFpF6OO7Cw9qxiIlynYS0zI3NWv2F8HxJHj81y2Ix9WodKmCw68BT8KDge4OUMVo3BDN2XVv794T6J82t3/hPwkIRyJ1o5wC2teSQTgob1lDBXI5AwgbifDKe/7Y3p2nn7KCebNmRVwnsVwtcjgFs78+2wDtHF2HVwZBedmbnm7j09JO9cK8glTikiz6H7v0vcQO19HcyDw62psJcV2c4HDncWw==",
        "CommandID": "BusinessPayment",
        "Amount": "200",
        "PartyA": "601342",
        "PartyB": "254741151005",
        "Remarks": "Pay Salary",
        "QueueTimeOutURL": my_endpoint + "timeout",
        "ResultURL": my_endpoint + "result",
        "Occasion": "Salary"
    }

    res = requests.post(endpoint, json = data, headers = headers)
    return res.json()

@app.route('/lnmo')
def init_stk():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = _access_token()
    headers = { "Authorization": "Bearer %s" % access_token }
    my_endpoint = "/lnmo"
    Timestamp = datetime.now()
    times = Timestamp.strftime("%Y%m%d%H%M%S")
    password = "174379" + "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919" + times
    datapass = base64.b64encode(password.encode('utf-8'))

    data = {
        "BusinessShortCode": "174379",
        "Password": datapass,
        "Timestamp": times,
        "TransactionType": "CustomerPayBillOnline",
        "PartyA": "", # fill with your phone number
        "PartyB": "174379",
        "PhoneNumber": "", # fill with your phone number
        "CallBackURL": my_endpoint,
        "AccountReference": "TestPay",
        "TransactionDesc": "HelloTest",
        "Amount": 2
    }

    res = requests.post(endpoint, json = data, headers = headers)
    return res.json()

@app.route('/lnmo', methods=['POST'])
def lnmo_result():
    data = request.get_data()
    f = open('lnmo.json', 'a')
    f.write(data)
    f.close()

@app.route('/b2c/result', methods=['POST'])
def result_b2c():
    data = request.get_data()
    f = open('b2c.json', 'a')
    f.write(data)
    f.close()

@app.route('/b2c/timeout', methods=['POST'])
def b2c_timeout():
    data = request.get_json()
    f = open('b2ctimeout.json', 'a')
    f.write(data)
    f.close()

@app.route('/c2b/val', methods=['POST']) # This is for validation
def validate():
    data = request.get_data() # get the data
    f = open('data_v.json', 'a') # write to file
    f.write(data) # write mode or you can write mode that you want
    f.close() # Then close the file

@app.route('/c2b/con', methods=['POST']) # This is for confirmation
def confirm():

    data = request.get_json() # get the data
    f = open('data_c.json', 'a') # write to file
    f.write(data) # write mode or you can write mode that you want
    f.close() # Then close the file


def _access_token():
    global consumer_key    
    global consumer_secret

    #base_url = '' # used for domain names or any other ip address one may require to use
    consumer_key = 'wT7uN60NNAiJA9KyXb7AepQAOkaRcotC'
    consumer_secret = 'cwVyibjc98Cfh1wM'


    consumer_key = consumer_key
    consumer_secret = consumer_secret
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'

    r = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = r.json()
    return data['access_token']


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)