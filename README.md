# people_detection

Project for the Data Analytics Pipeline Course (spring 2019) taught by Prof. Adam Kelleher

## Description/Goal of the Project

* The primary objective is to help students/conference attendees navigate themselves to empty seats in the room without disrupting the class
* By identifying the presence and location of people in a room, we can identify which seats are occupied/empty
* The current version uses static images that we captured from a video that we took of our class. This can be set up to run on real time images obtained from a camera
* We followed a master/dev/feature branch structure on GitHub, requiring a PR from feature branch to dev and one approving review

## Important Links

All the components of the project and the integration has been explained below. Also, there are instructions below to get the application working on local. For demonstration, the producer, consumer and the prediction service have been set up on AWS EC2. The dashboard has been set up on Azure. Listing the important links here for easy access before moving on to explanation of the project

#### Model Play Ground:

https://people-detection.azurewebsites.net/model

#### Dashboard:

https://people-detection.azurewebsites.net

#### REST API for predictions (used by the dashboard):
The endpoint to get the response from the prediction service (tornado app) hosted on AWS EC2 is:  
http://3.211.225.41:8080

## Final Architecture

![Final Project Architecture](/dashboard/public/test/Pipeline.jpg)

## JIRA

https://toydemoproject.atlassian.net/jira/software/projects/PD/boards/14


## Components and their description

* Producer – Service that pulls images from local storage and sends the images to a Kafka topic
* Kafka Server – a single node Kafka cluster, with one topic and a single partition. The cluster is managed using Zookeeper, so that we can use multiple nodes, topics and partitions if necessary
* Consumer – Polls images from Kakfa and makes request to Azure API service to predict on images. Stores the prediction locally
    * Input – Camera Image
    * Output – Array of probabilities of seats being occupied
* Prediction Service - Reads the output stored by the consumer and makes it available through a REST API set up using Tornado
    * Input – Array of probabilities of seats being occupied
    * Output – Server hosting the predictions for the dashboard to read from
* UI/Dashboard – Frontend js app displaying color intensity corresponding to probability of the seat being occupied
    * Input – Array of probabilities of seats being occupied
    * Output – web application indicating occupied/empty seats

## Integration of Components

1) The producer service pulls from local storage, and sends an image to a Kafka topic.
2) The consumer service continuously checks the Kafka topic for new images written.
3) When a new image is picked up, it sends the image to a pre-trained model endpoint hosted on Azure.
4) The endpoint returns bounding boxes for the contents of the image.
5) The consumer service parses the bounding boxes and writes relevant information to local storage.
6) The prediction service reads the output stored by the consumer service and makes it available through a REST API set up using Tornado
6) When the dashboard service is hit by an inbound request, it requests the information it needs for visualizations from the Tornado app

## Producer Service

To execute, from command line run:
`> python3 producer_storage.py video_to_images 5 loop`

The storage producer works the images in local storage. The script is written for images with filenames of a certain format: `frame_60.jpg` where 60 indicates the frame number  
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


## Consumer + Prediction Service

To execute, from command line run:
```
> python3 consumer_storage.py /Users/user1/Downloads
> python3 prediction_service.py /Users/user1/Downloads
```
The **consumer_storage.py** is the script that sets up the consumer and the **prediction_service.py** is the script that sets up the prediction service. Both scripts have an optional argument **PREDICTION_DIR_PATH** that can be passed during script execution. This is the temporary path (directory can either be relative or absolute) where the prediction is pickled and stored by the consumer service and consequently the path from which the prediction service reads the prediction before it makes it available over the REST API. If this is not passed, it needs to be set **manually** in the scripts. Note that the value defaults to a local path on my machine currently and **has** to be updated. Please ensure that the arguments contain the same path on both scripts

## Prediction API (used by the consumer)

* Azure allows you to manually label several images, and then use transfer learning on a pretrained model to be able to label the rest of your images
* We labeled a small subset of our images, and achieved strong performance

## Kafka Component: Installation and Usage

Make sure you have pykafka installed:
`pip install pykafka`

Then, install kafka. If you're on Mac, it's as simple as:
```
brew cask install homebrew/cask-versions/java8
brew install kafka
```

This should also automatically install zookeeper, a dependency of kafka and which handles cluster management (i.e. election of new leaders, if running multiple nodes). We'll first start a zookeeper server, then a kafka server:

```
zkServer start
kafka-server-start /usr/local/etc/kafka/server.properties
```

Create a new kafka topic; for simplicity, no replication and 1 partition:
`kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test`

We're ready to use pykafka to produce and consume from our topic. Once ready to delete the topic and spin down kafka:
```
/usr/local/bin/kafka-topics --delete --topic test --zookeeper localhost:2181
zkServer stop
```
Finally, CTRL+C in the terminal window in which you have kafka up to kill it.


## Kafka Settings Update

Before the producer and consumer are run, the kafka settings need to be updated to handle large messages. As we are dealing with images, the messages are larger than the default setting provided by Kafka. For this, go to the server.properties file inside the config folder and add the following properties:
```
message.max.bytes=104857600
replica.fetch.max.bytes=104857600
max.message.bytes=104857600
```
Note that the config folder will be present inside the kafka installation folder

## Dashboard

```
Change directory:
     > cd dashboard

Install dependencies:
     > npm install

Make your own configure file from config_template.json:
     > config.json

Run the app (Windows):
     > SET DEBUG=dashboard:* & npm start

Or, run the app (Mac OS/Linux):
     > npm start
```
