var socket = require("socket.io-client")("http://localhost:5000");
var Crypto = require('cryptojs');
Crypto = Crypto.Crypto;
var IV = 'This is an IV456';
var MODE = new Crypto.mode.CFB(Crypto.pad.ZeroPadding);

var p = 1;
var g = 1;
var salt = "111111111111111"
message = "google.com"
var input_bytes = Crypto.charenc.UTF8.stringToBytes(message);
var options = {iv: Crypto.charenc.UTF8.stringToBytes(IV), asBytes: true, mode: MODE};


var secret_1 = Math.floor(Math.random() * (100 - 1) + 1);
var secret_2 = Math.floor(Math.random() * (100 - 1) + 1);
var secret_3 = Math.floor(Math.random() * (100 - 1) + 1);
var shared_1 = Math.pow(g, secret_1) % p;
var shared_2 = Math.pow(g, secret_2) % p;
var shared_3 = Math.pow(g, secret_3) % p;

console.log(secret_1, secret_2, secret_3);

var response_node_1 = null;
var response_node_2 = null;
var response_node_3 = null;

var shared_secret_1 = null;
var shared_secret_2 = null;
var shared_secret_3 = null;

socket.on('connect', function() {
      console.log("Sharing and creating keys...");
      console.log("Sending this data ", {p: p, g: g, s1: shared_1, s2: shared_2, s3: shared_3, jump:1,
         second_host: 'localhost', second_port: 6000,
         third_host: 'localhost', third_port: 7000,
         authorization: '...'
       });
      socket.emit('create_conection', {p: p, g: g, s1: shared_1, s2: shared_2, s3: shared_3, jump:1,
         second_host: 'localhost', second_port: 6000,
         third_host: 'localhost', third_port: 7000,
         authorization: 'BN24ZEnP4Z0gqflvxE9MOu0h11zfyAuK/La6i6sjaxaW1L6K0PpLf7Xwu69taWvFOR/28UOygxN64Ld+cMRuiPadwMBSygtwTw0lye3H5lCm11/aQV+IJnNFc/m5yHZuGddgT5j3qyqSsZ7kzCZe2YRC/f2vJ4asUyEjelid/b8='
       });
      socket.on('response1', function (response1) {
        console.log('I received a private message by node ', response1['jump']);
        response_node_1 = response1;

      });
      socket.on('response2', function (response2) {
        console.log('I received a private message by node ', response2['jump']);
        response_node_2 = response2;
      });
      socket.on('response3', function (response3) {
        console.log('I received a private message by node ', response3['jump']);
        response_node_3 = response3;
      });
    });

//seguramente se deberia usar una promesa o algo asi para esperar a las respuestas

setTimeout(function() {
  console.log("\n\nresponse 1.. ", response_node_1['shared_node']);
}, 5000);

//computing shared keys

setTimeout(function() {
  shared_secret_1 = Math.pow(response_node_1['shared_node'], secret_1) % p;
}, 5000);
setTimeout(function() {
  shared_secret_2 = Math.pow(response_node_2['shared_node'], secret_2) % p;
}, 5000);
setTimeout(function() {
  shared_secret_3 = Math.pow(response_node_3['shared_node'], secret_3) % p;
}, 5000);


setTimeout(function() {
  console.log("creating keys...");
  var KEY_1 = salt + shared_secret_1;
  var KEY_2 = salt + shared_secret_2;
  var KEY_3 = salt + shared_secret_3;

  var key_1 = Crypto.charenc.UTF8.stringToBytes(KEY_1);
  var key_2 = Crypto.charenc.UTF8.stringToBytes(KEY_2);
  var key_3 = Crypto.charenc.UTF8.stringToBytes(KEY_3);

  var encrypted_1 = Crypto.AES.encrypt(input_bytes, key_1, options);
  var encrypted_hex_1 = Crypto.util.bytesToHex(encrypted_1);
  var encrypted_2 = Crypto.AES.encrypt(encrypted_hex_1, key_2, options);
  var encrypted_hex_2 = Crypto.util.bytesToHex(encrypted_2);
  var encrypted_3 = Crypto.AES.encrypt(encrypted_hex_2, key_3, options);
  var encrypted_hex_3 = Crypto.util.bytesToHex(encrypted_3);


  console.log("message encrypted: ")


  console.log("Sending request...");
  socket.emit('decrypt_and_send', {
    jump:1, second_host: 'localhost', second_port: 6000,
    third_host: 'localhost', third_port: 7000,
    uuid1 : response_node_1['uuid'],
    uuid2 : response_node_2['uuid'],
    uuid3 : response_node_3['uuid'],
    message: encrypted_hex_3,
    authorization: 'BN24ZEnP4Z0gqflvxE9MOu0h11zfyAuK/La6i6sjaxaW1L6K0PpLf7Xwu69taWvFOR/28UOygxN64Ld+cMRuiPadwMBSygtwTw0lye3H5lCm11/aQV+IJnNFc/m5yHZuGddgT5j3qyqSsZ7kzCZe2YRC/f2vJ4asUyEjelid/b8='
   });
  socket.on('content', function (content) {
    console.log('The response is ', content);

}, 6000);

setTimeout(function() {

});}, 10000);

