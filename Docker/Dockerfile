# Use an official Ubuntu as a base image
FROM ubuntu:jammy

ARG DEBIAN_FRONTEND=noninteractive

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
        build-essential \
		cmake \
        gdb \
		libglfw3 \
		libglfw3-dev \
		iputils-ping \
		iproute2 \
		iptables \
		wget

		
#RUN cd eprosima_dds && ./install.sh

RUN wget https://go.dev/dl/go1.21.4.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.21.4.linux-amd64.tar.gz
RUN echo "PATH=$PATH:/usr/local/go/bin" >> ~/.bashrc


