#Dockerfile

#The base image is the official Python image
FROM python:3.10


#Declare some environment vars
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#Defining the working directory inside of the container
WORKDIR /code

#Install some system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*


#Install the project dependencies
COPY ./tictactoe_server/requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt 

#Copy the current project files into the container at the /code path
COPY . /code/
