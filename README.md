# Distributed Log Replication V3

Final iteration that adds request retries, message ordering, and deduplication. Additional tasks (heartbeats and quorum append) were also implemented using Consul Checks.

![task](https://user-images.githubusercontent.com/25267308/210255638-c5c0c502-f3a6-48e0-9951-9a762902e1d6.png)

## Features

New in v3:
* supports smart retries with exponential backoff, based on health reports from the services
* health checks via regular HTTP requests from Consul
* quorum append that turns main node into read-only if majority nodes is unavailable

New in v2:
* supports write_concern parameter
* performs messages deduplication 
* guarantees the total ordering of messages, does not return messages after gaps
* one of the secondary nodes has a delay of 10 seconds (input through an env variable)

New in v1:
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

## Verify Retry Logic

Retries are implemented with an unlimited number of attempts and a smart delay logic that uses exponential backoff. A decision was made not to introduce any timeout from the master. Instead, the client will be waiting forever until the response is received. It will be the responsibility of the client to use a certain timeout whenever making a request.

### Acceptance Check

1. Start M + S1 + S2 and stop S2. It is important to first start all secondaries so that Consul discovers the URLs of all services we are trying to use.
![stat](https://user-images.githubusercontent.com/25267308/210262987-06f2eed3-3ef7-4b24-94aa-8a746dc7680a.png)

2. Send (Msg1, W=1) - Ok
![img-1](https://user-images.githubusercontent.com/25267308/210263282-3d13f4c7-850c-4c0c-93f3-7da2aa6e80e4.png)

3. Send (Msg2, W=2) - Ok
![img-2](https://user-images.githubusercontent.com/25267308/210263297-b25f9e78-4c03-4d62-a3ef-3d67adb427f4.png)

4. Send (Msg3, W=3) - Wait. The client is blocked until the node becomes available:
![img-3](https://user-images.githubusercontent.com/25267308/210263633-e9b41b10-fc87-4e3d-82db-0a987982364d.png)

In the logs, we can see a continuos retry running in background:
![img](https://user-images.githubusercontent.com/25267308/210263816-20eaa3fa-4db0-4db8-8659-884493cfdbc1.png)

5. Send (Msg4, W=1) - Ok. The client that is running in parallel is not blocked by the blocked one.
![img-4](https://user-images.githubusercontent.com/25267308/210264057-60559bc0-1399-44ec-bdf5-b1641857f631.png)

Now we can see in the logs several pending retries for the above requests:
![retry](https://user-images.githubusercontent.com/25267308/210263993-7d2c0731-ea4f-4631-89c6-8279253ce7ab.png)

6. Start S2. Check messages on S2 - [Msg1, Msg2, Msg3, Msg4]
![img-5](https://user-images.githubusercontent.com/25267308/210264235-642cd84d-0426-4ad5-8502-94258124d9a9.png)

On the above screenshot, we can see that all messages that S2 missed due to unavailability are replicated after (re)joining the master. Consequent GET request:
![img-6](https://user-images.githubusercontent.com/25267308/210264348-2f14245f-6c7d-4069-ae12-1e7f15b1d80d.png)

It shows that message deduplication and global ordering works!

## Verify Health Report

As soon as all nodes are started, we can send a /health GET request to main to see the health report:
![report](https://user-images.githubusercontent.com/25267308/210262004-ff3c7d02-5ad1-465c-b3a5-7df972eb9dbb.png)

There will also be ongoing heartbeat requests coming from Consul to all secondary services every 20 seconds:
![req](https://user-images.githubusercontent.com/25267308/210262092-685a1387-1cfb-4776-9c2e-7f1a394a3ffc.png)

Please note that sometimes it might take up to 40 seconds for the health checks to properly update the report because of the frequency of the health checks. This is why sometimes on start we might need to wait a bit longer for health checks to catch up and find all healthy services.

Let's run `docker-compose stop secondary-node-1` and verify the health check:
![check](https://user-images.githubusercontent.com/25267308/210264561-b344498c-5ede-45b2-b5a0-78308c871c7f.png)


## Verify Quorum Append

Let's stop both secondaries so that we don't have quorum (1 nodes out of 3). The health check report:
![rep](https://user-images.githubusercontent.com/25267308/210262544-955a7635-b1c3-4a36-8862-da615e556535.png)

Now let's try to insert a message, and see that it is not allowed:

![inse](https://user-images.githubusercontent.com/25267308/210264662-43f1003b-cc72-4df5-a28a-ec90293399c4.png)


## Verify Write Concern Parameter

Below is the screenshot of requests used for verification:
![screen](https://user-images.githubusercontent.com/25267308/205514029-eed13d21-d1f2-4732-b2ae-5c67e538ecfd.png)

# Verify other parameters

Checklist from v2:
* With write_concern=2, Secondary and Master are displaying different values for the duration of the delay
* With write_concern=3, Secondary and Master are displaying the same values
* Supports deduplication and ordering

Checklist from v1:
* Master exposes simple HTTP server with POST and GET methods to insert and read messages
* Secondary exposes simple HTTP server with POST and GET methods to insert (aimed for Master only) and read messages
* After each POST request, the message is replicated to every Secondary server available
