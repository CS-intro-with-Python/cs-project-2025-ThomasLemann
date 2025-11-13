[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/DESIFpxz)
# CS_2025_project

## Description

The idea of project is to create a browser game (puzzle), where user can log in and try to solve puzzles. Each puzzle is a picture cut into pieces.

## Setup

Describe the steps to set up the environment and run the application. This can be a bash script or docker commands.

```
docker build -t new_image:latest .
docker run -p 8080:8080 -d --name container_1 new_image:latest
pip install -r requirements.txt
python client.py

```

## Requirements

Python 3.11

## Features

Describe the main features the application performs.

* Feature 1: log in system
* Feature 2: different levels: from change of pictures to number of pieces
* Feature 3: ability to create your own puzzles (user can send picture to server, and it can be then cut into pieces and solved as a puzzle game)

## Git

I will have my project on a main branch

## Success Criteria

Describe the criteria by which the success of the project can be determined
(this will be updated in the future)

* Criteria 1: working system of sign up and log in
* Criteria 2: puzzles work correctly and write a message when completed
* Criteria 3: users can create new puzzle games

## Railway
cs-project-2025-thomaslemann-production.up.railway.app
