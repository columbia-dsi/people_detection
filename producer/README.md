## Image Producer
Source Data:
1) Shakeshack Images - obtained by making a get request to an image service
2) Images from Class - Video converted to frames and stored locally

There are two scripts written for the two different sources
**producer_shakeshack.py** for the Shakeshack Images
**producer_storage.py** for the Images in local storage

Before using any of these scripts:
1) Make sure Kafka is installed (read the main README)
2) Make sure all requirements are installed
3) Set up Kafka broker on `127.0.0.1:9092`
4) Set up a topic named `people-detection`
5) If the host IP/port or topic name is different, update the scripts accordingly
6) Make sure the Kafka config file settings are updated for large file sizes (refer to main README)

### Shakeshack Producer
This script sets up the producer for the Shakeshack images  
This script takes one argument:  
*IMAGE_FREQUENCY:* Number of seconds between consecutive requests  
to the camera service for images to be sent to Kafka.  
Default value: 5  

```
python3 producer_shakeshack.py 5
```

### Storage Producer
This script sets up the producer for the images in local storage.  
The script is written for images with filenames of a certain format:  
`frame_60.jpg` where 60 indicates the frame number  
Ex: frame_60, frame_120, etc  

This script takes three arguments:  
*IMAGE_DIR_PATH:* Path to the folder containing the images  
Default value: `video_to_images`  
*IMAGE_FREQUENCY:* Number of seconds between consecutive reads from local storage  
for images to be sent to Kafka.  
Default value: `5`  
*PRODUCER_TYPE:* `loop` or `random`  
loop: Read images in the folder in a loop in the order of frame number  
random: Read random images from the folder  
Default value: `loop`  

```
python3 producer_storage.py video_to_images 5 loop
```
