from flask import Flask, jsonify, request

from Crypto.PublicKey import RSA
from datetime import import datetime

from diff

app = Flask(__name__)


def validateToken(token):
    with open('private.pem','r') as priv_pem:
        priv_key = RSA.importKey(priv_pem.read())
        decripted_token = priv_key.decrypt(token)
        date_token = datetime.strptime(decripted_token,'%m/%d/%Y')
        current_date = datetime.now()
        if(decripted_token < current_date):
            return False
        else:
            return True


def establish_diffie_hellman():
    pass

@app.route("/enroute", methods={'POST'})
def enroute():
    token = request.headers.get('authorization', None)
    valid = validateToken(token)
    if valid:
        # Establish diffie hellman connection


        # Receive message


        # Decrypt message


        # Send message to the next node
