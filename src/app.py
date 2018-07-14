from flask import Flask, jsonify, request

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime
from random import randint

from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

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

@socketio.on('establish-dh')
def establish_diffie_hellman(data):
    # Generate id of the transaction
    # Receive two shared primes
    # Generate random private secret
    import pdb; pdb.set_trace()
    p = request.form.get('p')
    g = request.form.get('g')
    node_private_secret = randint(0,100) 
    # send A = g^a mod p
    node_shared_node = (g**private_secret) % p
    # Receive client secret
    client_shared_secret = request.form.get('s')
    # Shared secret
    shared_secret = (client_shared_secret ** node_private_secret) % p
    
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(shared_secret, AES.MODE_CFB, iv)
    print(cipher, iv)
    return (cipher, iv)

@app.route("/enroute", methods={'POST'})
def enroute():
    token = request.headers.get('authorization', None)
    valid = validateToken(token)
    if valid:
        pass
    return ('hola')
        # Establish diffie hellman connection


        # Receive message


        # Decrypt message


        # Send message to the next node

if __name__ == '__main__':
    socketio.run(app)
