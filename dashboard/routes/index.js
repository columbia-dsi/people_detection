var express = require('express');
var router = express.Router();
 var request = require('request');


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
  request({
        host: 'https://southcentralus.api.cognitive.microsoft.com',
        path: '/customvision/v3.0/Prediction/eff56ac8-0f36-41d9-93a9-da19396b0f30/detect/iterations/Iteration2_ppl_focus/image',
        method: 'POST',
        headers: {
            'Prediction-Key': '5e0cd4f967c142ca90153bc8e3b6773e',
            'Content-Type': 'application/octet-stream'
        },
        body: req.body.pic
      },
      function (error, response, body) {
          if (!error && response.statusCode == 200) {
              console.log(body);
              res.render('model', { title: 'Model', content: body});
          }
          else{
             console.log(error);
          }
      });

});


router.post('/model/post/url', function(req, res, next) {
  request({
        host: 'https://southcentralus.api.cognitive.microsoft.com',
        path: '/customvision/v3.0/Prediction/eff56ac8-0f36-41d9-93a9-da19396b0f30/detect/iterations/Iteration2_ppl_focus/image',
        method: 'POST',
        headers: {
            'Prediction-Key': '5e0cd4f967c142ca90153bc8e3b6773e',
            'Content-Type': 'application/json'
        },
        body: { 
          'Url': req.body.url
        }
      },
      function (error, response, body) {
          if (!error && response.statusCode == 200) {
              console.log(body);
              res.render('model', { title: 'Model', content: body});
          }
          else{
             console.log(error);
          }
      });
});


module.exports = router;
