from flask import Flask, jsonify, request, render_template

from Crypto.PublicKey import RSA
from Crypto.Cipher import AES
from Crypto import Random
from datetime import datetime
from random import randint

import base64
import uuid
from flask_socketio import SocketIO, emit, send
from socketIO_client import SocketIO as cli
from socketIO_client import LoggingNamespace


app = Flask(__name__)

socketio = SocketIO(app)
salt_key = '111111111111111'

keys_list = {} # It will keep the pair uuid : shared_secret
received_keys = [] # It will contain the key as a intermedium storage between
                    # the callback from the node 3 and 1, since no direct communication
                    # is possible.
                    # TODO: Change websocket library to avoid this problem.


def validateToken(token):
    '''This method is used to validate the token that is in the headers.
    '''
    with open('private.pem','r') as priv_pem:
        priv_key = RSA.importKey(priv_pem.read())
        decripted_token = priv_key.decrypt(token)
        date_token = datetime.strptime(decripted_token,'%m/%d/%Y')
        current_date = datetime.now()
        if(decripted_token < current_date):
            return False
        else:
            return True

def on_connect():
    print('connect')

def on_connect_node(*args):
    ''' This method is used as a callback when a nested node generates a key.
    '''
    print ('Receiving call',args)
    if args:
        print ('sending..')
        jump = args[0].get('jump')
        print ('Receiving data from node ', args)
        if(jump==2):
            emit('response'+str(jump), args[0])
        elif(jump==3):
            received_keys.append(args)
            emit('response'+str(jump), args[0])

@socketio.on('connect')
def connection():
    print('Connection established')


@socketio.on('create_key')
def retreive_key(data):
    '''This method is used in order to compute the shared_secret from the node.
        It is used to compute the shared secret in DH.
    '''
    p = data.get('p')
    g = data.get('g')
    jump = data.get('jump')
    node_private_secret = randint(0,100)
    node_shared_node = (g**node_private_secret) % p
    if (jump==2):
        client_shared_secret = data['s2']
    elif (jump==3):
        client_shared_secret = data['s3']
    shared_secret = (client_shared_secret ** node_private_secret) % p
    key = salt_key + str(shared_secret)
    identifier = str(uuid.uuid4())
    keys_list[identifier]=key
    return dict(shared_node=node_shared_node, uuid=identifier, jump=jump)

@socketio.on('create_conection')
def establish_diffie_hellman(data):
    '''This method is used to create the key exchange with the client recursively
        Using websockets, generating shared secrets with each node (3).
    '''
    # Receive two shared primes
    # Generate random private secret
    jump = data.get('jump')
    response = 'response '
    if (jump==1):
        p = data.get('p')
        g = data.get('g')
        client_shared_secret = data['s1']
        host = data['second_host']
        port = data['second_port']
        data['jump'] += 1
        node_private_secret = randint(0,100)
        # send A = g^a mod p
        node_shared_node = (g**node_private_secret) % p
        identifier = str(uuid.uuid4())
        print ('generating key 1')
        emit('response'+str(jump), dict(shared_node=node_shared_node, uuid=identifier, jump=jump))
        # Shared secret
        shared_secret = (client_shared_secret ** node_private_secret) % p
        key = salt_key + str(shared_secret)
        keys_list[identifier]=key

        print(shared_secret)
        with cli(host, port, LoggingNamespace) as my_client:
            my_client.on('connect', on_connect)
            my_client.emit('create_key', data, on_connect_node)
            my_client.emit('create_conection', data, on_connect_node)
            my_client.wait(seconds=3)
    elif(jump==2):
        data['jump'] += 1
        host = data['third_host']
        port = data['third_port']
        with cli(host, port, LoggingNamespace) as my_client:
            my_client.on('connect', on_connect)
            my_client.emit('create_key', data, on_connect_node)
            my_client.wait(seconds=1)
            next_key = received_keys.pop()
            next_key[0]['jump'] = jump+1
            print('sending...key', next_key)
            return next_key


def generate_key_and_decrypt(uuid, message):
    '''Search into the uuid dict of the node, once it has the shared_secret
        From DH. It creates the key and decrypt it.
    '''
    key = keys_list.get(uuid, None)
    if key:
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(key, AES.MODE_CFB, iv)
        return cipher.decrypt(message)

@socketio.on('decrypt_and_send')
def decript_and_send(data):
    '''This method decrypt the message and send it to the next node.
        It is recursively called
    '''
    jump = data.get('jump')
    message = data.get('message')
    if (jump==1):
        data['jump'] += 1
        uuid = data.get('uuid1')
        host = data['second_host']
        port = data['second_port']
        decrypted_message = generate_key_and_decrypt(uuid, message)
        data['message'] = decrypted_message
        with cli(host, port, LoggingNamespace) as my_client:
            my_client.on('connect', on_connect)
            my_client.emit('decrypt_and_send', data)
            my_client.wait(seconds=3)
    elif (jump==2):
        data['jump'] += 1
        uuid = data.get('uuid2')
        host = data['third_host']
        port = data['third_port']
        decrypted_message = generate_key_and_decrypt(uuid, message)
        data['message'] = decrypted_message
        with cli(host, port, LoggingNamespace) as my_client:
            my_client.on('connect', on_connect)
            my_client.emit('decrypt_and_send', data)
            my_client.wait(seconds=1)
    elif (jump==3):
        # end of the way
        uuid = data.get('uuid3')
        host = data['third_host']
        port = data['third_port']
        decrypted_message = generate_key_and_decrypt(uuid, message)
        print ('Message decrypted: ', decrypted_message)

@app.route("/enroute", methods={'POST'})
def enroute():
    token = request.headers.get('authorization', None)
    valid = validateToken(token)
    if valid:
        pass
        # allow comunication
    else:
        pass
        # return 404

if __name__ == '__main__':
    socketio.run(app, port=5000)
