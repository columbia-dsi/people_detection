## Image Consumer
There are three versions of scripts written:    
**1) consumer_shakeshack.py** for the Shakeshack Images    
**2) consumer_storage.py** for the Images in local storage    
**3) consumer_storage_tornado.py** for the Images in local storage plus the consumer is a tornado web application that serves the predictions    

Note that the scripts run in an infinite loop consuming messages. For the consumer_storage_tornado script, there is an **IMAGE_FREQUENCY** parameter which dictates how often the consumer consumes a message. This is required because the consumer runs on a single thread but also needs to act as a tornado app that serves the predictions required for the dashboard. The **IMAGE_FREQUENCY** is the duration for which execution is yielded between message consumption - this allows the tornado app to respond to the requests coming its way. The current version of the script makes the prediction available on port 8080 on localhost. This can be set up on cloud to be accessible over the internet.    

Before using any of these scripts:
1) If the host IP/port for the Kafka broker is not `127.0.0.1:9092` or if the topic name is not `people-detection`, update the consumer script
2) In the environment in which the script is launched, set the environment variable `AZURE_VIS_KEY` to the key required to access the Azure model service. The script picks up the key from this environment variables and is required for the consumer to function. Contact Kevin Gao if you need the key
3) If using the **consumer_storage_tornado.py** script, there is an optional argument **IMAGE_FREQUENCY** that can be passed during script execution like this. Note that the value defaults to `30`    
```
python3 consumer_storage_tornado.py 30
```
