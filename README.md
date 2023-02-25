# UDP test

This is a quick thing I put together for testing UDP packet sending behaviours.

Interestingly, if a message is delayed by the server and sent after the client times out,
the message is still received client side. An actual client would need to proactively manage response validity.

I did try randomly generating multiple identical repsonses from the server, that only caused confusion for this simple client.
Writing a more complex client capable of recognising and discarding duplicate server packets, and tracking those for
which no response was received, would become necessary.

## NAT

The other exercise I wanted to attempt was NAT traversal. To mock this out, I run the client from within a docker container:

The Dockerfile (replacing `<HOST IP>` with the IP of my machine):

```Dockerfile
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 busybox
ADD udp_test.py /udp_test.py

CMD python3 /udp_test.py client <HOST IP>
```

The test:

```sh
docker build -t nattest:latest .
docker run -d --rm --name=nattest_container nattest:latest
python3 udp_test.py server
docker stop nattest_container
```

The server responds successfully to the client (with the appropriate firewall port opened!).

