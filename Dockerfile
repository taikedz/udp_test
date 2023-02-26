FROM alpine:latest
RUN apk update && apk add python3
ADD udp_test.py /udp_test.py
ENTRYPOINT ["python3", "/udp_test.py"]

