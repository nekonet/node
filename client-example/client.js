var socket = require("socket.io-client")("http://localhost:5000");

socket.on('connect', function() {
      console.log("Sharing and creating keys...");
      socket.emit('create_conection', {p: 4, g: 23, s1: 3, s2: 1, s3: 3, jump:1, second_host: 'localhost', second_port: 6000, third_host: 'localhost', third_port: 7000 });
      socket.on('response1', function (from) {
        console.log('I received a private message by ', from);
      });
      socket.on('response2', function (from) {
        console.log('I received a private message by ', from);
      });
      socket.on('response3', function (from) {
        console.log('I received a private message by ', from);
      });
    });

socket.on('connect', function() {
  console.log("Sending request...");
  socket.emit('create_conection', {
    jump:1, second_host: 'localhost', second_port: 6000,
    third_host: 'localhost', third_port: 7000,
    uuid1 : 'fillme',
    uuid2 : 'fillme',
    uuid3 : 'fillme',
    message: 'triple_encrypted_message'
   });
  socket.on('decrypt_and_send', function (content) {
    console.log('The response is ', content);
  });
});
