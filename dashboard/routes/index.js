var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('../config.json');
var fs = require('fs');
var getAbsolutePath = require('path').resolve;


/* GET home page. */
router.get('/', function(req, res, next) {
  res.render('dashboard', { title: 'Dashboard' });
});

router.get('/index', function(req, res, next) {
  res.render('index', { title: 'Express' });
});

/*Model*/

router.get('/model', function(req, res, next) {
  res.render('model', { title: 'Model' });
});



router.post('/model/post/image', function(req, res, next) {
  //call the custom vision model
  //console.log('pic:', req.body.pic);
  //TODO: Kafka -> Publish images under ./public/test/
  //TODO: Kafka -> calling the model API
  const path = './public/test/' + req.body.pic;
  const imagePath = getAbsolutePath(path);
  //console.log('imagePath:', imagePath);
  var raw = fs.createReadStream(imagePath);
  request({
        uri: config.model.api.prediction.image.uri,
        method: 'POST',
        headers: {
            'Prediction-Key': config.model.api.prediction.image.key,
            'Content-Type': 'application/octet-stream'
        },
        body: raw
      },
      function (error, response, body) {
          if (!error && response.statusCode == 200) {
              res.render('model', { title: 'Model', content: body});
          }
          else{
             console.log('error:',error);
             console.log('body:', body);
          }
      });

});


router.post('/model/post/url', function(req, res, next) {
  //call the custom vision model
  request({
        uri: config.model.api.prediction.url.uri,
        method: 'POST',
        headers: {
            'Prediction-Key': config.model.api.prediction.url.key,
            'Content-Type': 'application/json'
        },
        json: true,
        body: { 
          'Url': req.body.url
        }
      },
      function (error, response, body) {
          if (!error && response.statusCode == 200) {
             //console.log('body:', JSON.stringify(body));
             res.render('model', { title: 'Model', content: body});
          }
          else{
             console.log('error:',error);
             console.log('body:', body);
          }
      });
});




router.get('/map', function(req, res, next) {
  //Integration: Convert the model API result -> seat map
  
  //Pick the first image (Or overwritten by Kafka publishing)
  const folder = './public/test/';

  fs.readdir(folder, function(err, items) {
    var path = folder + '/' + items[0];
    console.log("Find: " + path);

    const imagePath = getAbsolutePath(path);
    var raw = fs.createReadStream(imagePath);
    request({
      uri: config.model.api.prediction.image.uri,
      method: 'POST',
      headers: {
          'Prediction-Key': config.model.api.prediction.image.key,
          'Content-Type': 'application/octet-stream'
      },
      body: raw
    },
    function (error, response, body) {
        if (!error && response.statusCode == 200) {
            res.render('map', { title: 'Map', content: body});
        }
        else{
            console.log('error:',error);
            console.log('body:', body);
        }
    });

  });


});


module.exports = router;
