FROM postgres:latest

# install PGVector
RUN apt-get update
RUN apt-get install -y git
RUN apt-get install -y build-essential
RUN apt-get install -y postgresql-server-dev-16

WORKDIR /tmp
RUN git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git
WORKDIR /tmp/pgvector
RUN make
RUN make install
