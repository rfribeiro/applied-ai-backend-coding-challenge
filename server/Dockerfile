FROM tensorflow/tensorflow:latest-gpu

RUN apt-get update && apt-get install -y build-essential libpq-dev libpqxx-dev \
	libtbb-dev libevent-dev libboost-all-dev git-core cmake


# download and compile AMUN
WORKDIR /home/app/
RUN git clone https://github.com/marian-nmt/amun.git
RUN mkdir -p /home/app/amun/build
WORKDIR /home/app/amun/build
RUN cmake .. -DCUDA=OFF
RUN cmake --build .

RUN rm -rf /home/app/server

# Create the working directory (and set it as the working directory)
RUN mkdir -p /home/app/server
WORKDIR /home/app/server

# Copy the source code into the container
COPY ./build/consumer /home/app/server/consumer
RUN cp /home/app/amun/build/amun /home/app/server/amun
COPY ./en-de /home/app/server/en-de
COPY ./conf/consumer.conf.json /home/app/server/consumer.conf.json

CMD chmod 775 consumer

#CMD ["/bin/bash", "./home/app/server/consumer","/home/app/server/consumer.conf.json"]
