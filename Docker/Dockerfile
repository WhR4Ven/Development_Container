# Use an official Ubuntu as a base image
FROM ubuntu:jammy

# Install necessary packages
RUN apt-get update && \
    apt-get install -y \
        build-essential \
        cmake \
        gdb
		
RUN apt install wget
RUN wget https://www.eprosima.com/index.php/component/ars/repository/eprosima-fast-dds/eprosima-fast-dds-2-12-0/eprosima_fast-dds-v2-12-0-linux-tgz?format=raw	
RUN mv eprosima_fast-dds-v2-12-0-linux-tgz\?format\=raw eprosima_dds_lib.tgz 
RUN mkdir eprosima_dds
RUN tar -xzf eprosima_dds_lib.tgz -C eprosima_dds 
RUN cd eprosima_dds && ./install.sh

RUN wget https://go.dev/dl/go1.21.4.linux-amd64.tar.gz
RUN tar -C /usr/local -xzf go1.21.4.linux-amd64.tar.gz
RUN echo "PATH=$PATH:/usr/local/go/bin" >>  ~/.bashrc