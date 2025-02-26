# CodeGenie
## Project Overview
The Intelligent IDE is an AI-powered development environment designed to enhance developer productivity. It automates code generation, test creation, and debugging with advanced AI-driven suggestions, making bug fixing seamless. The project also integrates continuous build and integration processes to streamline development workflows.

To ensure a consistent and scalable setup, Docker is used for containerized deployment, enabling easy installation and execution across different environments.
## AI Assistant
![image](https://github.com/user-attachments/assets/2fceda79-d2f5-4c8c-b2a1-4271daa31f50)
## Run code
![image](https://github.com/user-attachments/assets/2b562e88-5baf-46cc-81c0-df48ee9dfd5c)
## Generate tests
![image](https://github.com/user-attachments/assets/ad32a485-6418-4b16-b286-616897ff3c0a)
## Debug code
![image](https://github.com/user-attachments/assets/d04fd2d0-b72b-4200-993b-c8b57bb9cf9b)
## Build and deploy if test cases passed
![image](https://github.com/user-attachments/assets/1c4d9c96-3659-46c9-b2e2-2d262d6d676c)



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
To view the setup required for frontend, go to Intelligent_IDE/llm-app/frontend repository linked
Now the project is up and running with Docker! 🎉

