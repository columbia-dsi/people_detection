## Image Producer
Source Data:
1) Shakeshack Images - obtained by making a get request to an image service
2) Images from Class - Video converted to frames and stored locally

There are two scripts written for the two different sources    
**1) producer_shakeshack.py** for the Shakeshack Images    
**2) producer_storage.py** for the Images in local storage    

Note that both scripts run in an infinite loop. The service/app needs to be killed to stop producing images. For the producer producing images from local storage, there are two options: option one is to produce images in the order of frames(inferred from the file name) and loop through the folder in an infinite loop while option two is to pick up random images from the folder in an infinite loop. Both scripts take an IMAGE_FREQUENCY parameter which dictates how often an image needs to be produced and sent to Kafka

Before using any of these scripts:
1) Make sure Kafka is installed (read the main README)
2) Make sure all requirements are installed
3) Set up Kafka broker on `127.0.0.1:9092`
4) Set up a topic named `people-detection`
5) If the host IP/port or topic name is different, update the scripts accordingly
6) Make sure the Kafka config file settings are updated for large file sizes (refer to main README)

### Shakeshack Producer
This script sets up the producer for the Shakeshack images. This script takes one argument:  
**IMAGE_FREQUENCY:** Number of seconds between consecutive requests to the camera service for images to be sent to Kafka.  
Default value: `5`  

```
python3 producer_shakeshack.py 5
```

### Storage Producer
This script sets up the producer for the images in local storage. The script is written for images with filenames of a certain format: `frame_60.jpg` where 60 indicates the frame number  
Ex: frame_60.jpg, frame_120.jpg, etc  

This script takes three arguments:  
**IMAGE_DIR_PATH:** Local path (can either be relative or absolute) to the folder containing the images  
Default value: Directory in my local path - so this **has** to either be passed or manually updated in the script  
**IMAGE_FREQUENCY:** Number of seconds between consecutive reads from local storage for images to be sent to Kafka.  
Default value: `5`    
**PRODUCER_TYPE:** `loop` or `random`  
*loop:* Read images in the folder in a loop in the order of frame number  
*random:* Read random images from the folder  
Default value: `loop`  

```
python3 producer_storage.py /Users/user1/Downloads/video_to_images 5 loop
```
