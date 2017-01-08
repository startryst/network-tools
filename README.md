Network monitoring and diagnostic tools developed by python mainly for MacOS/Linux platform

If you would like to play the tools instead of dive into the source code, please check out below:
	1. Released executable files in /dist directory, by default only compatible for MacOS, if you need to run for other platform, you have two options:
		a. Install python 3.x with the required imported modules
		b. send me an email(9034785@qq.com) for your request on other platform
	2. Once you have downloaded the executable file in your MacOS, please give those executable file "X" permission by issuing below command:
		a. navigate your terminal console into the directory where the executable file been downloaded
		b. chmod +x filename (filename is the executable file's name)

If you would like to dive into the source code and collaborate with me:
	1. All finished codes will be in the master branch
	2. Other branches are for testing new features

trace_as.py
	1. Trace for a destination and print out/save the path info together with AS number and AS number info
	2. Query for different external system: whois to MeritRADb and Cymru, RESTAPI to ipip.net
	3. Multiprocessing of trace and whois activity for all the hops along the path
	4. RESTAPI to ipip.net has concurrent connection detection and restriction, so need to pause for 1s for each query
	5. If the ASN appears to be numeric and different with formers(except Not Found, *, Private, Timeout), 'AS BORDER' will be print out

trace_as_step.py
	1. Same as trace_as.py, but change the way from multiprocessing into step by step query
	2. Will be somehow a little bit longer compareed with trace_as.py, but will be more stable under narrow bandwidth condition