# Tratoli API Task

## API Endpoints

Below are the available API endpoints for the project:

### Authentication

- `POST /api/auth/login` - Log in to the application.
- `POST /api/auth/logout` - Log out from the application.
- `POST /api/auth/refresh-token` - Refresh the authentication token.
- `POST /api/auth/register` - Register a new user.

### User Profile

- `GET /api/detail/profile` - Get the user profile details.
- `PUT /api/detail/update-profile/` - Update the user profile details.

### API Documentation

- `/swagger` - Access the Swagger UI for interactive API documentation.
- `/redoc` - Access the ReDoc UI for alternative API documentation.

### Task Management

- `GET /api/tasks/` - Get a list of tasks.
- `GET /api/tasks/{id}/` - Get details of a specific task by its ID.
- `POST /api/tasks/` - Create a new task.
- `PUT /api/tasks/{id}/` - Update a specific task by its ID.
- `DELETE /api/tasks/{id}/` - Delete a specific task by its ID.
- `GET /api/tasks/export/` - Export the tasks.
- `GET /api/tasks/report/` - Generate a report of tasks.

## Project Structure
```bash
.
├── Dockerfile
├── docker-compose.yml
├── manage.py
├── requirements.txt
├── taskmanager
│   ├── __init__.py
│   ├── asgi.py
│   ├── celery.py
│   ├── celeryconfig.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tasks
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── consumers.py
│   ├── management
│   │   └── commands
│   │       ├── __init__.py
│   │       └── generate_tasks.py # This file generates fake records for tasks
│   ├── migrations/
│   ├── models.py
│   ├── routing.py
│   ├── serializers.py
│   ├── tasks.py
│   ├── tests.py
│   └── views.py
└── users
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── migrations/
    ├── models.py
    ├── serializers.py
    ├── tests.py
    └── views.py
```
## Project Setup and Installation
1. Clone the project
2. Install the docker using this  [link](https://docs.docker.com/engine/install/).
3. Run the docker container using below command:-
```bash
docker-compose up --build -d
```

## Screenshots
### API Response
- `POST /api/auth/register`
<img src="screenshots/register.png" alt="Create User" />
<br><br>

- `POST /api/auth/login`
<img src="screenshots/login.png" alt="Login User" />
<br><br>

- `POST /api/auth/refresh-token`
<img src="screenshots/refresh_token.png" alt="Refresh Token" />
<br><br>

- `POST /api/auth/logout`
<img src="screenshots/logout.png" alt="Logout User" />
<br><br>

- `GET /api/detail/profile`
<img src="screenshots/get_profile.png" alt="Get User Profile" />
<br><br>

- `PUT /api/detail/update-profile`
<img src="screenshots/update_profile.png" alt="Update User Profile" />
<br><br>

- `GET /api/tasks/`
<img src="screenshots/list_tasks.png" alt="List all Tasks" />
<br><br>

- `GET /api/tasks/{id}`
<img src="screenshots/retrieve_task.png" alt="Retrieve a Task" />
<br><br>

- `POST /api/tasks/`
<img src="screenshots/create_task.png" alt="Create a Task" />
<br><br>

- `PUT /api/tasks/{id}`
<img src="screenshots/update_task.png" alt="Update a Task" />
<br><br>

- `DELETE /api/tasks/{id}`
<img src="screenshots/delete_task.png" alt="Delete a Task" />
<br><br>

- `GET /api/tasks/report/`
<img src="screenshots/get_task_report.png" alt="Generate Task Report" />
<br><br>

- `GET /api/tasks/export/`
<img src="screenshots/export_task_csv.png" alt="Export Task CSV" />
<br><br>

- `GET /swagger`
<img src="screenshots/swagger.png" alt="Swagger Endpoint" />
<br><br>

- `GET /redoc`
<img src="screenshots/redoc.png" alt="Redoc Endpoint" />
<br><br>

- `GET /WS`
<img src="screenshots/ws.png" alt="Websocket Endpoint" />
<br><br>


### Task Creation Mail
<img src="screenshots/mail.png" alt="Mail Screenshot" />
<br><br>

### Rate Limiting
<img src="screenshots/rate_limiting.png" alt="Rate Limiting Screenshot" />
<br><br>

### Dummy Task Generation Script
<img src="screenshots/task_generation.png" alt="Task Generation Output Screenshot" />
<br><br>