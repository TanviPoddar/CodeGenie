# CodeGenie
# Project Setup and Running Guide

This guide provides step-by-step instructions to set up, build, and run the project using Docker.

## Prerequisites

Ensure you have the following installed:

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/) (if using `docker-compose.yml`)

## Clone the Repository

```sh
git clone <repository_url>
cd <repository_name>
```

## Build and Run the Docker Containers

### 1. Run the Application with Docker Compose

Simply run the following command to build and start all services:

```sh
docker-compose up --build
```

This command will:

- Build the necessary images
- Start both the frontend and backend containers
- Automatically link services as per the `docker-compose.yml` configuration

> The `-d` flag can be added to run the containers in detached mode:
>
> ```sh
> docker-compose up -d --build
> ```

### 2. Verify Running Containers

Check if the containers are running:

```sh
docker ps
```

## Stopping and Removing Containers

### Stop the Containers

```sh
docker-compose down
```

This command stops and removes all running containers, networks, and volumes created by `docker-compose up`.

## Common Issues & Fixes

### 1. Module Not Found Errors (Dependencies Missing)

Run:

```sh
docker-compose down --volumes
docker-compose up --build
```

### 2. Port Conflicts

Check for running containers using `docker ps` and stop any conflicting ones:

```sh
docker stop <container_id>
docker rm <container_id>
```

### 3. Check Docker Logs for Errors

```sh
docker logs <container_name>
```

## Accessing the App

Once the container is running, access the application in your browser at:

```
http://localhost:3000
```

## Running the Backend

To start the backend manually, navigate to the backend folder and run:

```sh
cd backend
python app.py
```

## Additional Commands

### Restart the Containers

```sh
docker-compose restart
```

### View Logs in Real-Time

```sh
docker logs -f <container_name>
```

### Enter the Running Container

```sh
docker exec -it <container_name> /bin/sh
```

---

Now the project is up and running with Docker! 🎉

