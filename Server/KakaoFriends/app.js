//for socket
const net = require('net');
//for json, url encoding parser
const bodyParser = require('body-parser');
const express = require('express');
const app = express();
const port = process.env.PORT || 7979;
const server = app.listen(port, function(){
	console.log("Express server has started on port 7979");
});
const request = require('request');
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({
	extended:true
}));

//etri api
const fs = require('fs');
const content_config = fs.readFileSync('config').toString();
const configuration = content_config.split('\n');
let url = configuration[0];
var access_key = configuration[1];
var analysisCode = 'morp';
var etri_morpheme = function(res, user, msg, bot){
	var requestJson = {
		'access_key': access_key,
		'argument': {
			'text': msg,
			'analysis_code': analysisCode
		}
	};
	var options = {
		url: url,
		body: JSON.stringify(requestJson),
		headers: {'Content-Type': 'application/json; charset=UTF-8'}
	};
	request.post(options, function(error, response, body){
		if(error != null){
			console.log(error);
		}
		if(response.statusCode == 200){
			msg = '';
			json_body = JSON.parse(body);
			if ('return_object' in json_body){
				result = json_body['return_object']['sentence'][0]['morp'];
				for (key in result){
					let type = result[key]['type'];
					if(type == 'NNG' || type == 'VV'){
						msg += ' ' + result[key]['lemma'] + '_' + result[key]['type'];
					}	
				}
				console.log(msg);
			}
			chatscript_client(res, user, msg, bot);
		}
	});
};

//chatscript connection part
const cs_host = '127.0.0.1';
const cs_port = 1024;

var chatscript_client = function(res, user, msg, bot){
	let client = new net.Socket();
	let buf_user = new Buffer(user);
	console.log('user : ' + buf_user.toString());
	let buf_bot = new Buffer(bot);
	console.log('bot : ' + buf_bot.toString());
	let buf_msg = new Buffer(msg);
	console.log('msg : ' + buf_msg.toString());
	let buf_length = buf_user.length + buf_bot.length + buf_msg.length;
	let temp = 0;
	let result = new Buffer(buf_length + 3);
	buf_user.copy(result, 0, 0, buf_user.length);
	temp += buf_user.length;
	result[temp] = '\x01';
	buf_bot.copy(result, temp + 1, 0, buf_bot.length);
	temp += buf_bot.length + 1;
	result[temp] = '\x01';
	buf_msg.copy(result, temp + 1, 0, buf_msg.length);
	temp += buf_msg.length + 1;
	result[temp] = '\x01';
	console.log(result.toString());	
	client.connect(cs_port, cs_host, function(){
		console.log('Connected');
		client.write(result);
	});
	client.on('data', function(data){
		console.log('Received : ' + data);
		res.send({message:{text:data.toString()}});
		client.destroy();
	});
	client.on('close', function(){
		console.log('Connection closed');
	});
};

app.get('/keyboard', function(req, res){
	res.send(JSON.stringify({type:'text'}));
});

app.post('/message', function(req, res){
	console.log(req.body.content);
	//etri_morpheme(res, 'Kwanwoong Yoon', req.body.content, 'harry');
	chatscript_client(res, 'Kwanwoong Yoon', req.body.content, 'Travot');
});
