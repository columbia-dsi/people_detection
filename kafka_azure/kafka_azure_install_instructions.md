## Using Powershell

On Mac, first install powershell by running `brew cask install powershell`. Once you have powershell installed, run `sudo pwsh` and then `Install-Module -Name Az -AllowClobber`. This will install azure modules into Powershell, which are required for the following script.

Next, you'll follow the instructions below to spin up an HDInsight Kafka cluster that is accessible publicly. 

https://docs.microsoft.com/en-us/azure/hdinsight/kafka/apache-kafka-connect-vpn-gateway#vpnclient

## Manual Instructions

First, create an account on Microsoft Azure. (A student account gives you $100 to play with.)

Now, set up a storage account from the lefthand bar. For the purposes of our experimentation, the only setting that needs to be changed from default is turning off secure transfer. This removes the requirement for using HTTPs when services communicate with storage. You'll also make a new resource group while doing this; I named mine "kafka" but it can be anything.

Then, set up a virtual network (analogous to a VPC on AWS). You'll first need to choose an address space, which is specified using CIDR notation. In short, in CIDR notation you specify how many available IP addresses you'd like to have. A complete network address looks like "192.168.15.21/32" and represents a single IP address in its own subnet. The last number (32) is the network prefix; if you choose a number less than 32, then the difference is how many bits you have available for addressing. For example, if you choose 192.168.15.0/24, then you'll have 256 bits: 32 - 24 = 8, and 2^8 is 256. This gives us the range 192.168.15.0 - 192.168.15.255. In the *Address space* field, input 192.168.15.0/24, choose the existing kafka resource group, and create a default subnet using the same address range as the virtual network. 

Finally, we can set up our hdinsight kafka cluster. It's a series of forms. On "Basics" I named the cluster azureKafka. You'll select the Cluster type to be Kafka 1.1 with HDI 3.6. Specify a good cluster login password. Choose the kafka resource group, not NetworkWatcher. Make sure that you choose the same location that you made the virtual network in; for me, this was East US. On the next screen, choose the virtual network you created and its associated subnet. On the next screen, choose the storage account you created. Don't choose any applications. On cluster size, reduce the worker nodes to 3 and standard disks to 1. Once you create the cluster, note that you'll be billed per hour (from your credits) so work fast if you're prototyping! 

However, because this is in a virtual network, it can't be accessed publicly. You could spin up an instance in the same virtual network, but for prototyping purposes, it's better to follow the instructions in the "Using Powershell" section.



