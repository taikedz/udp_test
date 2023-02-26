# UDP test

This is a quick thing I put together for testing UDP packet sending behaviours.

Interestingly, if a message is delayed by the server and sent after the client times out,
the message is still received client side.

I discovered that an actual client would need to proactively manage response validity; in this iteration
I implemented a message stash that allows the client to register what it sent, and allow it to time out.
If the client eventually receives the response it expected, it can check to see whether it wants to allow
that response to be valid anymore based on time.

## NAT

The other exercise I wanted to attempt was NAT traversal. To mock this out, I run the client from within a docker container:

```sh
# Terminal Session 1
python3 udp_test.py server


# Terminal Session 2
docker build -t nattest:latest .
docker run -d --rm --name=nattest_container nattest:latest client <HOST IP>
# see the server is responding
docker stop nattest_container
```

The server responds successfully to the client (with the appropriate firewall port opened!).

What I want to futher test is, if the server delays more than N seconds, is there an eventual a NAT response failure (client no longer sees the response)?
