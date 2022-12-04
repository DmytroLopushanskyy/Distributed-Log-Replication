# Distributed Log Replication V2

Continuation of the previous task is to create one main node and any number of secondary nodes that are going to receive logs.

![task](https://user-images.githubusercontent.com/25267308/205513892-57c88398-6705-49b7-9606-ecf2b1a286d9.png)

## Features

New in v2:
* supports write_concern parameter
* performs messages deduplication 
* guarantees the total ordering of messages, does not return messages after gaps
* one of the secondary nodes has a delay of 10 seconds (input through an env variable)

From v1:
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

## Verify Write Concern Parameter

Below is the screenshot of requests used for verification:
![screen](https://user-images.githubusercontent.com/25267308/205514029-eed13d21-d1f2-4732-b2ae-5c67e538ecfd.png)


# Verify other parameters

New checklist:
* With write_concern=2, Secondary and Master are displaying different values for the duration of the delay
* With write_concern=3, Secondary and Master are displaying the same values
* Supports deduplication and ordering

Checklist from v1:
* Master exposes simple HTTP server with POST and GET methods to insert and read messages
* Secondary exposes simple HTTP server with POST and GET methods to insert (aimed for Master only) and read messages
* After each POST request, the message is replicated to every Secondary server available
