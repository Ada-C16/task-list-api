# Task List API

## Deployed API

Task List is deployed on Heroku: https://much-wow-app.herokuapp.com/tasks

## Technologies
I used `Python`, `Flask` ((including Migrate and Alembic), `SQLAlchemy`, `PostgreSQL`, `Postman`, `Heroku`

## Overview

There's so much we want to do in the world! When we organize our goals into smaller, bite-sized tasks, we'll be able to track them more easily, and complete them!

With Task List, we'll be able to create, read, update, and delete tasks as long as we have access to the Internet and our API is running!

This app is able to:

- Sort tasks
- Mark them as complete
- Get feedback about our task list through Slack
- Organize tasks with goals

... and more!

## Behavior and Structure

- Create models
- Create conventional RESTful CRUD routes for a model
- Read query parameters to create custom behavior
- Create unconventional routes for custom behavior
- Apply knowledge about making requests in Python, to call an external API (Slack) inside of an API
- Apply knowledge about environment variables
- Creating a one-to-many relationship between two models
- Write unit tests

## Setup and Installation

Please see the [setup guide](https://github.com/Ada-C16/task-list-api/blob/master/ada-project-docs/setup.md)

## CRUD for One Model

### Create a Task: Valid Task With `null` `completed_at`

As a client, I want to be able to make a `POST` request to `/tasks` with the following HTTP request body

```json
{
  "title": "A Brand New Task",
  "description": "Test Description",
  "completed_at": null
}
```

and get this response:

`201 CREATED`

```json
{
  "task": {
    "id": 1,
    "title": "A Brand New Task",
    "description": "Test Description",
    "is_complete": false
  }
}
```

so that I know I successfully created a Task that is saved in the database.

### Get Tasks: Getting Saved Tasks

As a client, I want to be able to make a `GET` request to `/tasks` when there is at least one saved task and get this response:

`200 OK`

```json
[
  {
    "id": 1,
    "title": "Example Task Title 1",
    "description": "Example Task Description 1",
    "is_complete": false
  },
  {
    "id": 2,
    "title": "Example Task Title 2",
    "description": "Example Task Description 2",
    "is_complete": false
  }
]
```

### Get Tasks: No Saved Tasks

As a client, I want to be able to make a `GET` request to `/tasks` when there are zero saved tasks and get this response:

`200 OK`

```json
[]
```

### Get One Task: One Saved Task

As a client, I want to be able to make a `GET` request to `/tasks/1` when there is at least one saved task and get this response:

`200 OK`

```json
{
  "task": {
    "id": 1,
    "title": "Example Task Title 1",
    "description": "Example Task Description 1",
    "is_complete": false
  }
}
```

### Get One Task: No Matching Task

As a client, I want to be able to make a `GET` request to `/tasks/1` when there are no matching tasks and get this response:

`404 Not Found`

No response body.

### Update Task

As a client, I want to be able to make a `PUT` request to `/tasks/1` when there is at least one saved task with this request body:

```json
{
  "title": "Updated Task Title",
  "description": "Updated Test Description",
}
```

and get this response:

`200 OK`

```json
{
  "task": {
    "id": 1,
    "title": "Updated Task Title",
    "description": "Updated Test Description",
    "is_complete": false
  }
}
```

Note that the update endpoint does update the `completed_at` attribute. This will be updated with custom endpoints implemented in Wave 03.

### Update Task: No Matching Task

As a client, I want to be able to make a `PUT` request to `/tasks/1` when there are no matching tasks with this request body:

```json
{
  "title": "Updated Task Title",
  "description": "Updated Test Description",
}
```

and get this response:

`404 Not Found`

No response body

### Delete Task: Deleting a Task

As a client, I want to be able to make a `DELETE` request to `/tasks/1` when there is at least one saved task and get this response:

`200 OK`

```json
{
  "details": "Task 1 \"Go on my daily walk 🏞\" successfully deleted"
}
```

### Delete Task: No Matching Task

As a client, I want to be able to make a `DELETE` request to `/tasks/1` when there are no matching tasks and get this response:

`404 Not Found`

No response body.

### Create a Task: Invalid Task With Missing Data

#### Missing `title`

As a client, I want to be able to make a `POST` request to `/tasks` with the following HTTP request body

```json
{
  "description": "Test Description",
  "completed_at": null
}
```

and get this response:

`400 Bad Request`

```json
{
  "details": "Invalid data"
}
```

so that I know I did not create a Task that is saved in the database.

#### Missing `description`

If the HTTP request is missing `description`, we should also get this response:

`400 Bad Request`

```json
{
  "details": "Invalid data"
}
```

#### Missing `completed_at`

If the HTTP request is missing `completed_at`, we should also get this response:

`400 Bad Request`

```json
{
  "details": "Invalid data"
}
```


