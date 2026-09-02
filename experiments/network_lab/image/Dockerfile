FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install -y \
      frr \
      frr-pythontools \
      iproute2 \
      iputils-ping \
      traceroute \
      tcpdump \
      netcat-openbsd \
      curl \
      procps \
      less \
      vim-tiny && \
    rm -rf /var/lib/apt/lists/*

CMD ["bash", "-lc", "tail -f /dev/null"]
