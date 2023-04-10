User Management
-----------------

Provides simple user management.

### Install requirements 
First of all to run the entire app you have to install [docker](https://docs.docker.com/engine/install/)

### Running

To make a first run, you need to create a common network for services (if you don't have yet).
It will be used by all local microservices, so that they can communicate with each other.
```
docker network create users_network
```

After that, feel free to start server (configs can be found in config/local.yaml): 
```
docker compose up server
```

Find the name of app server via checking ip of your users_network
```
docker network inspect users_network
```
Check port of you app server (in my case `user-manager-server-1`)
```
docker container port user-manager-server-1
```
so you can do it simple like `http://localhost:<your_app_server_port>/redoc`


### Documentation
You can test entire app (with auth) SwaggerUI OpenApi  `http://localhost:<your_app_server_port>/docs`