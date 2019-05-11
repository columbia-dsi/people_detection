## Manual Instructions

First, create an account on Microsoft Azure. (A student account gives you $100 to play with.)

Now, set up a storage account from the lefthand bar. For the purposes of our experimentation, the only setting that needs to be changed from default is turning off secure transfer. This removes the requirement for using HTTPs when services communicate with storage. You'll also make a new resource group while doing this; I named mine "kafka" but it can be anything.

Then, set up a virtual network (analogous to a VPC on AWS). You'll first need to choose an address space, which is specified using CIDR notation. In short, in CIDR notation you specify how many available IP addresses you'd like to have. A complete network address looks like "192.168.15.21/32" and represents a single IP address in its own subnet. The last number (32) is the network prefix; if you choose a number less than 32, then the difference is how many bits you have available for addressing. For example, if you choose 192.168.15.0/24, then you'll have 256 bits: 32 - 24 = 8, and 2^8 is 256. This gives us the range 192.168.15.0 - 192.168.15.255. In the *Address space* field, input 192.168.15.0/24, choose the existing kafka resource group, and create a default subnet using the same address range as the virtual network. 

