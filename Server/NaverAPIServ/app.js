var fs = require('fs');
var express = require('express');
var app = express();
const content_config = fs.readFileSync('config').toString();
const configuration = content_config.split('\n');
var client_id = configuration[0];
var client_secret = configuration[1];
var end_point = 'https://openapi.naver.com/v1/search/kin';

app.get('/search/kin', function(req, res){
    var api_url = end_point + '?query=' + encodeURI(req.query.query) + '&display=100&sort=sim&start=' + encodeURI(req.query.start);
    var request = require('request');
    var options = {
        url : api_url,
        headers : {'X-Naver-Client-Id' : client_id, 'X-Naver-Client-Secret' : client_secret}
    };
    request.get(options, function(error, response, body){
        if(!error & response.statusCode == 200){
            res.writeHead(200, {'Content-Type' : 'text/json;charset=utf-8'});
            res.end(body);
        }else{
            res.status(response.statusCode).end();
            console.log('error = ' + response.statusCode);
        }
    });
});

app.listen(8895, function(){
    console.log('http://localhost:8895, naver api app listening on port 8895');
});
