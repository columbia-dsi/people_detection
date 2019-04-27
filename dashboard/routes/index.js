var express = require('express');
var router = express.Router();
var request = require('request');
var config = require('../config.json');


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
  console.log('body:', JSON.stringify(req.body.pic));
  request({
        uri: config.model.api.prediction.image.uri,
        method: 'POST',
        headers: {
            'Prediction-Key': config.model.api.prediction.image.key,
            'Content-Type': 'application/octet-stream'
        },
        body: req.body.pic
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


module.exports = router;
