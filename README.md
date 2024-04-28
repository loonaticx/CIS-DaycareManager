# CIS3368 Final Project Part 1: Daycare API

Created by Erica Miller (2031854) for the Spring 2024 semester.

## Installation

This program was made with the SQLAlchemy, MySQL connector, and Flask packages.

Ensure you have the required dependencies downloaded by running the following command in this directory:

```
python -m pip install -r requirements.txt
```

## Usage

First, take a look at ``config/Config.py`` and check if the ``CONNECTION_MODE`` is what you intend.
The default value is ``REMOTE_SERVER``, which is the AWS server -- our final presenting database.
Other values such as ``LOCAL_FILE`` and ``LOCAL_MEMORY`` can be used for testing purposes.

Keep in mind that the program, including the utility and interface code, will interact with the database 
as determined by ``CONNECTION_MODE``.

To start the show, you can simply run:
```
python main.py
```

# [VIDEO LINK](https://www.youtube.com/watch?v=QTXyvSG_gTo)

Please note that you must send a GET request to localhost:5000/api/generate to generate an authentication cookie.
If you don't you will not be able to access any of the API.


To generate arbitrary daycares into the database, you can run the following:
```
python -m utils.DaycareGenerator
```

### Endpoints
```
/api/generate  # Generate auth token

/api/lookup/<facilityId>/<classroomId>/<teacherId>/<childId>

/api/lookup/facility  # All facilities

/api/lookup/classrooms  # All classroomss

```


---

[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-24ddc0f5d75046c5622901739e7c5dd533143b0c8e959d652212380cedb1ea36.svg)](https://classroom.github.com/a/WpQRsNaU)
