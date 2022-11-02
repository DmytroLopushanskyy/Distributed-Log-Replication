# Distributed Log Replication V1

The task is to create one main node and any number of secondary nodes that are going to receive logs.

![task](https://user-images.githubusercontent.com/25267308/199399372-dcfbfdf4-2bb8-4b0b-a9be-8619f3fd6f21.png)

## Features

* Solution is fully dockerized with docker-compose
* Satisfies all functional requirements
* Includes an additional Consul service for service discovery
* Includes a custom logger that nicely formats any output messages

## Start Application

To start application, please download, install, and launch Docker first.

Then use the following command:
```
docker-compose up --build
```

To verify that everything started correctly, please visit the following URL: http://localhost:8500/ui/dc1/services/consul/instances/consul-server/consul/health-checks

If the output is `Agent alive and reachable`, then Consul has successfully started, and you are good to go.

You should also see the following output that all services started correctly:  

![services](https://user-images.githubusercontent.com/25267308/199391834-04e68cb4-41e5-40e7-9565-02c90764ca4e.png)

## Verify Correctness

Checklist:
* Master exposes simple HTTP server with POST and GET methods to insert and read messages
* Secondary exposes simple HTTP server with POST and GET methods to insert (aimed for Master only) and read messages
* After each POST request, the message is replicated to every Secondary server available
* Master’s POST request should be finished only after receiving ACKs from all Secondaries (blocking replication approach)

Let's see the proof of the above:
![proof](https://user-images.githubusercontent.com/25267308/199400892-79bcee60-7d35-43cf-8611-45344404461f.png)
Here we can clearly see that after adding a 5 second timeout to both Secondaries, the request to Main took 10 seconds to complete.

