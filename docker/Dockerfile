FROM ubuntu:22.04

# Install Bitcoin Core
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN wget https://bitcoin.org/bin/bitcoin-core-26.0/bitcoin-26.0-x86_64-linux-gnu.tar.gz \
    && tar -xzf bitcoin-26.0-x86_64-linux-gnu.tar.gz \
    && install -m 0755 -o root -g root -t /usr/local/bin bitcoin-26.0/bin/* \
    && rm -rf bitcoin-26.0*

# Create bitcoin user
RUN useradd -r -m -s /bin/bash bitcoin

# Create data directory
RUN mkdir -p /home/bitcoin/.bitcoin && chown -R bitcoin:bitcoin /home/bitcoin

USER bitcoin
WORKDIR /home/bitcoin

# Expose RPC port
EXPOSE 8332

CMD ["bitcoind", "-txindex", "-rpcallowip=0.0.0.0/0", "-rpcbind=0.0.0.0"]

