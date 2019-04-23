# Unbabel Applied AI Backend Challenge

Hey 😄

Welcome to our Applied AI Backend Challenge repository. This README will guide you on how to participate in this challenge.

In case you are doing this to apply for our open positions for an Applied AI Software Engineer make sure you first check the available jobs at https://unbabel.com/jobs

Please fork this repo before you start working on the challenge. We will evaluate the code on the fork.

FYI: Please understand that this challenge is not decisive if you are applying to work at Unbabel. There are no right and wrong answers. This is just an opportunity for us both to work together and get to know each other in a more technical way.

## Challenge

1. Build a basic web app with a simple input field that takes an English (EN) input translates it to Spanish (ES).
2. When a new translation is requested it should add to a list below the input field (showing one of three status: requested, pending or translated)
3. The list should be dynamically ordered by the size of the translated messages

### Requirements

* Use Flask web framework
* Use PostgreSQL
* Create a scalable application.
* Use the Marian-decoder (C++ framework) as a way to translate from English to Spanish
* Use RabbitMQ to communicate in between your web application (python) and Marian (C++)
* Use C++ to build the wrapper that will manage the communication between Marian and RabbitMQ
* Have tests

### Notes

* Page load time shouldnt exceed 1 second
* You should not have to touch Marian code (the documentation for developers is almost non existing) but information on how to use Marian-decoder are available [here](https://github.com/marian-nmt/marian) and you should be able to understand the minimum on how to use marian-decoder
* There is no time limit for this challenge. However, we want to follow your progress so we advise that you share the fork as soon as possible, commit often and keep us updated. 


### Resources

* Marian - https://github.com/marian-nmt/marian
* RabbitMQ - https://www.rabbitmq.com/#getstarted
* Flask - http://flask.pocoo.org

## Activities

- [X] Flask input page
- [X] Flask publish input on RabbitMQ 
- [X] Flask save translation input on PostgreSQL 
- [X] C++ Wrapper definition
- [X] C++ Wrapper RabbitMQ consumer
- [X] Send JSON object to RabbitMQ from Flask 
- [X] Read JSON object to RabbitMQ from C++ Wrapper
- [X] C++ Update status translation on PostgreSQL
- [X] C++ Wrapper translation using Marian
- [X] C++ save translation on PostgreSQL server
- [X] Flask web page dinamically update from database
- [X] Flask web page pagination (removed)
- [X] Flask web page dinamically list
- [X] Flask web page memcache ??
- [ ] Flask web and C++ wrapper refactorying
- [X] Application configuration servers
- [X] Create Errors pages and test scenarios
- [X] Dockerize application
- [ ] Page localization support
- [ ] C++ wrapper batch translation ??
- [X] application deploy

## steps to RUN application
```
#update and install packages
sudo apt-get update && sudo apt-get install -y build-essential libpq-dev libpqxx-dev \
libtbb-dev libevent-dev libboost-all-dev git-core cmake docker python3-pip virtualenv

#install docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# docker user 
sudo usermod -aG docker rfribeiro

#install docker compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

#install app
# app
git clone https://github.com/rfribeiro/applied-ai-backend-coding-challenge.git

cd applied-ai-backend-coding-challenge

pip3 install --no-cache-dir -r web/requirements.txt

# create database dockerfile
cd web
python3 create_postgres_dockerfile.py
cd ..

cd server
mkdir build
cd build
cmake ..
cmake --build .
cd ../..

# download translation pre-trained model from drive
https://drive.google.com/open?id=1zlvHRWwlFGQsSdmYlImxskXHbB22zjmz
copy to "applied-ai-backend-coding-challenge/server/en-de" folder

# build dockers
sudo docker-compose build

# init database schema
sudo docker-compose run web bash
cd web
python instance/db_create.py
exit

# run dockers
sudo docker-compose run --rm translator ./consumer consumer.conf.json
```

