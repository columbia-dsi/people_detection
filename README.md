# people_detection
Project for Data Analytics Pipeline.

## Kafka Component: Installation and Usage

Make sure you have pykafka installed:
```pip install pykafka```

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
```kafka-topics --create --zookeeper localhost:2181 --replication-factor 1 --partitions 1 --topic test```

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

## Deployment
#### Model Play Ground:

https://people-detection.azurewebsites.net/model

#### Dashboard:

https://people-detection.azurewebsites.net

#### Consume API (Kafka on EC2)

http://3.211.225.41:8080

## Final Architecture

![Final Project Architecture](/dashboard/public/test/Pipeline.jpg)

## JIRA

https://toydemoproject.atlassian.net/jira/software/projects/PD/boards/14

