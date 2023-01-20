# WWF Backend System

The system will accept Camera trap images and pass them through the classification pipelines and generate the alerts for the users through SMS and/or Notifications.
The system includes the dashboard for summerising the different reports about recieved data.

## Technology Stack

- Server: **Ubuntu 18.4 LTS**
- Channel Service: **Redis**
- Database: **SQL (Postgres, MySQL etc.) or NoSQL (MongoDB)**
- Framework: **Django (Backend) & React (Frontend)**

## Projected Milestones

### Schema Definition
  - **Time Estimate:** 2 weeks
  - **Description:** The schema defines the models to represent the data assosiated with the camera trap images that needs to be stored in database.
  - **Examples:** Geo Location, Time of the Day, Number of detections etc.

### Data Recieving
  - **Time Estimate:** 1 week
  - **Description:** The Target APIs which will recieve and pass the camera trap images to the classification pipeline.

### Deployment for Staging
  - **Time Estimate:** 1 weeks
  - **Description:** Configuring and installing the required services on the server to host and serve the APIs publically.
  - **Examples:** Redis, NGINX, UWSGI, Database, etc. 

### Generating Alerts
  - **Time Estimate:** 1 weeks
  - **Description:** Implementing the Firebase Cloud Messages to generate alerts for the listening devices and testing. 

## Useful links:
  - [Django](https://www.djangoproject.com/)
  - [Django REST Framework](https://www.django-rest-framework.org/)
  - [Server Setup Guide](https://oliverelliott.org/article/computing/tut_setup_nginx_django/)
  - [FCM Django](https://github.com/xtrinch/fcm-django)
  - [django-push-notifications](https://pypi.org/project/django-push-notifications/1.2.1/)
