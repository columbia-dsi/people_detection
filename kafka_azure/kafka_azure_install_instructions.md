## Using Powershell

Note that these instructions will burn a lot of Azure credits if you leave the resources up! Be sure to eliminate them after prototyping.

On Mac, first install powershell by running `brew cask install powershell`. Once you have powershell installed, run `sudo pwsh` and then `Install-Module -Name Az -AllowClobber`. This will install azure modules into Powershell, which are required for the spinup script.

After that, you need to generate a self-signed certificate so that you can authenticate into the cluster. Instructions are here (https://docs.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-certificates-point-to-site) but they don't actually work because you can't install the module needed on Mac; instead, follow these instructions: https://docs.microsoft.com/en-us/azure/vpn-gateway/vpn-gateway-certificates-point-to-site-linux. To install strongswan on Mac, just `brew install strongswan`. Also install openssl if you don't have it. Finally, be sure to use `sudo` when running the `ipsec` commands:

```sudo ipsec pki --gen --outform pem > caKey.pem```
```sudo ipsec pki --self --in caKey.pem --dn "CN=VPN CA" --ca --outform pem > caCert.pem``` 

```openssl x509 -in caCert.pem -outform der | base64 -w0 ; echo```

```export PASSWORD="password"```
```export USERNAME="client"```

```sudo ipsec pki --gen --outform pem > "${USERNAME}Key.pem"```
```sudo ipsec pki --pub --in "${USERNAME}Key.pem" | ipsec pki --issue --cacert caCert.pem --cakey caKey.pem --dn "CN=${USERNAME}" --san "${USERNAME}" --flag clientAuth --outform pem > "${USERNAME}Cert.pem"```

```openssl pkcs12 -in "${USERNAME}Cert.pem" -inkey "${USERNAME}Key.pem" -certfile caCert.pem -export -out "${USERNAME}.p12" -password "pass:${PASSWORD}"```

Double click the client.p12 file you created, and add it to your login keychain. 

Next, you'll follow the instructions below to spin up an HDInsight Kafka cluster that is accessible publicly. These have been copied over into a separate file in this folder for convenience. I recommend choosing a very unique base name -- many parts of Azure require global uniqueness, which means that your names for resources need to be unique too. Also, provisioning the VPN Gateway and the HDInsight cluster may take up to 30 minutes for each, so don't get too worried if they take forever.  

https://docs.microsoft.com/en-us/azure/hdinsight/kafka/apache-kafka-connect-vpn-gateway#vpnclient

Once that's all done executing successfully (hopefully!), don't forget to return to the link above to configure the cluster for IP advertising (that's the section following all the Powershell code). On Mac, there are even more configuration steps to do this! You'll run this in powershell:

```$profile=New-AzVpnClientConfiguration -ResourceGroupName "kafka" -Name "VPNGateway" -AuthenticationMethod "EapTls"

$profile.VPNProfileSASUrl

```

If you download the .zip file from that URL, you'll have the information needed to complete these steps:

https://docs.microsoft.com/en-us/azure/vpn-gateway/point-to-site-vpn-client-configuration-azure-cert#installmac

Finally, once you retrieve the broker IPs, you should be able to use the Jupyter notebook in this directory to send data to and from the Kafka cluster.

## Manual Instructions

First, create an account on Microsoft Azure. (A student account gives you $100 to play with.)

Now, set up a storage account from the lefthand bar. For the purposes of our experimentation, the only setting that needs to be changed from default is turning off secure transfer. This removes the requirement for using HTTPs when services communicate with storage. You'll also make a new resource group while doing this; I named mine "kafka" but it can be anything.

Then, set up a virtual network (analogous to a VPC on AWS). You'll first need to choose an address space, which is specified using CIDR notation. In short, in CIDR notation you specify how many available IP addresses you'd like to have. A complete network address looks like "192.168.15.21/32" and represents a single IP address in its own subnet. The last number (32) is the network prefix; if you choose a number less than 32, then the difference is how many bits you have available for addressing. For example, if you choose 192.168.15.0/24, then you'll have 256 bits: 32 - 24 = 8, and 2^8 is 256. This gives us the range 192.168.15.0 - 192.168.15.255. In the *Address space* field, input 192.168.15.0/24, choose the existing kafka resource group, and create a default subnet using the same address range as the virtual network. 

Finally, we can set up our hdinsight kafka cluster. It's a series of forms. On "Basics" I named the cluster azureKafka. You'll select the Cluster type to be Kafka 1.1 with HDI 3.6. Specify a good cluster login password. Choose the kafka resource group, not NetworkWatcher. Make sure that you choose the same location that you made the virtual network in; for me, this was East US. On the next screen, choose the virtual network you created and its associated subnet. On the next screen, choose the storage account you created. Don't choose any applications. On cluster size, reduce the worker nodes to 3 and standard disks to 1. Once you create the cluster, note that you'll be billed per hour (from your credits) so work fast if you're prototyping! 

However, because this is in a virtual network, it can't be accessed publicly. You could spin up an instance in the same virtual network, but for prototyping purposes, it's better to follow the instructions in the "Using Powershell" section, which will also spin up a Virtual Gateway. 



