## Image Consumer
There are two modes of operation for the consumer plus prediction service for static images:   
**1) Single Service that acts both as the consumer and the prediction service**  
**2) Two separate services for the consumer and the prediction service**

For option 1, we need to run the **consumer_storage_tornado.py** script. This service receives messages from the Kafka topic, calls the Azure Model API, manipulates the response and then exposes the prediction using a REST API built using Tornado.

For option 2, we need to run both the **consumer_storage.py** script and the **prediction_service.py** script. The former script consumes messages from Kafka, calls the Azure Model API, manipulates the response and then saves the prediction to local storage. The latter script reads the predictions from local storage and exposes the prediction using a REST API built using Tornado.

The advantage of using option 2 is that the consumer and the prediction services can be scaled independently. Moreoever, as there are two processes but only one thread for execution in option 1, the REST requests sometimes receive a slow response (some latency) - more info on this at the end of the README. So the preferred option is option 2.

Note that the scripts run in an infinite loop consuming messages. The current version of the script makes the prediction available on port 8080 on localhost. This can be set up on cloud to be accessible over the internet.

Before using any of these scripts:
1) If the host IP/port for the Kafka broker is not `127.0.0.1:9092` or if the topic name is not `people-detection`, update the consumer script
2) In the environment in which the script is launched, set the environment variable `AZURE_VIS_KEY` to the key required to access the Azure model service. The script picks up the key from this environment variables and is required for the consumer to function. Contact Kevin Gao if you need the key
3) If using the **consumer_storage_tornado.py** script, there is an optional argument **IMAGE_FREQUENCY** that can be passed during script execution like this. Note that the value defaults to `30`    
```
python3 consumer_storage_tornado.py 30
```
4) If using the **consumer_storage.py** and the **prediction_service.py** scripts, there is an optional argument **PREDICTION_DIR_PATH** that can be passed during script execution. This is the temporary path (directory can either be relative or absolute) where the prediction is pickled and stored by the consumer service and consequently the path from which the prediction service reads the prediction before it makes it available over the REST API. If this is not passed, it needs to be set **manually** in the scripts. Note that the value defaults to a local path on my machine currently and **has** to be updated
```
python3 consumer_storage.py /Users/user1/Downloads
python3 prediction_service.py /Users/user1/Downloads
```
Please ensure that both the arguments contain the same path

**Note explaining why separate services is better:** For the consumer_storage_tornado script, there is an **IMAGE_FREQUENCY** parameter which dictates how often the consumer consumes a message. This is required because the consumer runs on a single thread but also needs to act as a tornado app that serves the predictions required for the dashboard. The **IMAGE_FREQUENCY** is the duration for which execution is yielded between message consumption - this allows the tornado app to respond to the requests coming its way


**Note:** If the shakeshack images are used, the **consumer_shakeshack.py** script can be used to run the consumer service. However, this service currently only receives images from Kafka and prints the image dimensions. It needs to be updated to make the call to the Model API and then host the results in a Tornado app before it can be used
