from app.models.task import Task
from app.models.goal import Goal
from app import db
from flask import Blueprint, jsonify, make_response, request
from datetime import datetime
import requests
# from requests import post
import os

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix=("/tasks"))
goals_bp = Blueprint("goals_bp", __name__, url_prefix=("/goals"))

@tasks_bp.route("", methods=["GET", "POST"])
#any time we make a request to our api and call localhost5000, we are going to run the function.
#what will run depends on if the client calls GET or POST
def handle_tasks(): #view function names should be unique
    if request.method == "GET":
        tasks = Task.query.all() #Task is a child of SQLA so we can use the query method, 
        #query is method from sqla, paired with .all, retrieves all rows from task table in database, from there SQLA will turn all those rows into instances
        #of the task class, and all method will return all instances of the Task class into a list, and that list is assigned to variable task
        #Task.query.all.sort?? we can order the result the result of our selection
        tasks_response = []
        for task in tasks: #<Task 2342> - returns object, if we want to see attributes we have to 
            #access the attributes. So we break down objhects in that list in dictionary so we can see each instance's attributes
            tasks_response.append({
                "id": task.task_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
            })
        
        sort_param = request.args.get("sort")
        if sort_param == "asc":
            tasks_response.sort(key=lambda t: t["title"])
            
        if sort_param == "desc":
            tasks_response.sort(key=lambda t: t["title"], reverse=True)

        return jsonify(tasks_response), 200 #describes respond of an endpoint, once we receive this request, what do we respond with
#take data we want to respond with and put it in a javascript object format aka JSON, turns data into JSON form b/c JSON is an accepted data type to communicate between two entities

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            # return make_response("400 Bad Request")
            return {"details": "Invalid data"}, 400
        
        new_task = Task(
            title= request_body["title"],
            description= request_body["description"],
            completed_at= request_body["completed_at"]
        )
        db.session.add(new_task)
        db.session.commit()

        return {
            "task": {
                "id": new_task.task_id,
                "title": new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True
            }
        }, 201


@tasks_bp.route("/<task_id>", methods= ["GET", "PUT", "DELETE"])
def handle_task(task_id):
    task = Task.query.get(task_id)
    if request.method == "GET":
        if task is None:
            return jsonify(None), 404
        elif task.goal_id == None:
            return {
                "task": {
                    "id": task.task_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            }
        else:
            # return jsonify(task), 200
             return {
                "task": {
                    "id": task.task_id,
                    "goal_id": task.goal_id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                }
            }

    elif request.method == "PUT":
        if task is None:
            return jsonify(None), 404
        else:
            form_data = request.get_json()

            task.title = form_data["title"]
            task.description = form_data["description"]

            db.session.commit()

        # return make_response(f"Book #{book.id} successfully updated")
            return {
                    "task": {
                        "id": task.task_id,
                        "title": task.title,
                        "description": task.description,
                        "is_complete": False if task.completed_at == None else True
                    }
                }
        



# def handle_book(book_id):
#     for book in books:
#         if book.id == book_id:
#            return {
#               "id": book.id,
#               "title": book.title,
#               "description": book.description
#           }

#  return {
#         "id": book.id,
#         "title": book.title,
#         "description": book.description
#     }

   

    if request.method == "DELETE":
        if task is None:
            return jsonify(None), 404
        # request_body = request.get_json() request body contains information to help conduct the actual request
        # ie post request requires data to determines how to actually create the task
        db.session.delete(task)
        db.session.commit()

        return {"details": f'Task {task.task_id} "{task.title}" successfully deleted'}

@tasks_bp.route("/<task_id>/mark_complete", methods= ["PATCH"])
#whatever function underneath will run when this route is called
#put updates the entire record and patch is used when you want to modify a particular property of a record

def mark_complete(task_id):

    task = Task.query.get(task_id)

    if task is None:
        return jsonify(None), 404
    
    title_of_task =  f"Someone just completed the task {task.title}" 
    
    requests.post("https://slack.com/api/chat.postMessage", data={"channel": "task-notifications", "channelid": "C02K8MA17KR", "text": title_of_task}, headers={"authorization": os.environ.get("SLACK_API_TOKEN")})
    #we have to use the os.environ.get to get the value of the variable becacuse this is an environment variable. We know it's an environment variable because we created it in env file - 
    #variable whose value is set outside of the regular program files and refers to something that has to do with operating system.

    task.completed_at = datetime.today()

    db.session.commit()

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False if task.completed_at == None else True
        }
    }

@tasks_bp.route("/<task_id>/mark_incomplete", methods= ["PATCH"])



def mark_incomplete(task_id):

    task = Task.query.get(task_id)
    # taskvariable = None
    if task is None:
        return jsonify(None), 404

    task.completed_at = None
    

    db.session.commit()

    return {
        "task": {
            "id": task.task_id,
            "title": task.title,
            "description": task.description,
            "is_complete": False if task.completed_at == None else True
        }
    }


# goals_bp = Blueprint("goals_bp", __name__, url_prefix=("/goals"))
@goals_bp.route("", methods=["GET", "POST"])
#any time we make a request to our api and call localhost5000, we are going to run the function.
#what will run depends on if the client calls GET or POST
def handle_goals(): #view function names should be unique
    if request.method == "GET":
        goals = Goal.query.all() #Task is a child of SQLA so we can use the query method, 
        #query is method from sqla, paired with .all, retrieves all rows from task table in database, from there SQLA will turn all those rows into instances
        #of the task class, and all method will return all instances of the Task class into a list, and that list is assigned to variable task
        #Task.query.all.sort?? we can order the result the result of our selection
        goals_response = []
        for goal in goals: #<Task 2342> - returns object, if we want to see attributes we have to 
            #access the attributes. So we break down objhects in that list in dictionary so we can see each instance's attributes
            goals_response.append({
                "id": goal.goal_id,
                "title": goal.title
            })
        return jsonify(goals_response)
        #put response in JSON format to be used by rest of Flask, include headers, etc
        #help turn raw data into response that Flask can use
        #Flask develops web applications and includes features that helps you interface more easily with interfaces and defining APIs, ie glue code that helps our app
        #application that work with other libraries that work with website

    elif request.method == "POST":
        request_body = request.get_json()
        if "title" not in request_body:
            # return make_response("400 Bad Request")
            return {"details": "Invalid data"}, 400

        new_goal = Goal(
            title= request_body["title"]
        )
        db.session.add(new_goal)
        db.session.commit()

        return {
            "goal": {
                "id": new_goal.goal_id,
                "title": new_goal.title
            }
        }, 201

@goals_bp.route("/<goal_id>", methods= ["GET", "PUT", "DELETE"])
def handle_goal(goal_id):
    goal = Goal.query.get(goal_id)
    if request.method == "GET":
        if goal is None:
            return jsonify(None), 404
        else:
             return {
                "goal": {
                    "id": goal.goal_id,
                    "title": goal.title
                }
            }

    elif request.method == "PUT":
        if goal is None:
            return jsonify(None), 404
        else:
            form_data = request.get_json()

            goal.title = form_data["title"]

            db.session.commit()

        # return make_response(f"Book #{book.id} successfully updated")
            return {
                    "goal": {
                        "id": goal.goal_id,
                        "title": goal.title
                    }
                }
   
    if request.method == "DELETE":
        if goal is None:
            return jsonify(None), 404
        # request_body = request.get_json() request body contains information to help conduct the actual request
        # ie post request requires data to determines how to actually create the task
        db.session.delete(goal)
        db.session.commit()

        return {"details": f'Goal {goal.goal_id} "{goal.title}" successfully deleted'}

@goals_bp.route("/<goal_id>/tasks", methods= ["GET", "POST"])
def handle_goal_tasks(goal_id):
#we always pass goal id because every task is related to a goal
#the goal is the one, tasks are the many

    goal = Goal.query.get(goal_id)
    if goal is None:
        # return "Author not found", 404
        return jsonify(None), 404

    if request.method == "GET":
        tasks_response = []
        for task in goal.tasks:
            tasks_response.append(
                {
                "id": task.task_id, #references variable from line 286
                "goal_id": task.goal_id,
                "title": task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True
                }
            )
        goal_response = {
            "id": goal.goal_id,
            "title": goal.title,
            "tasks": tasks_response
        }
    
        return jsonify(goal_response)
        
    elif request.method == "POST":
        request_body = request.get_json()#takes request_body and transforms out of json format into python dictionaries and lists
        # requested_goal = Goal.query.get(id=goal_id)
        task_ids= []
        for task_id in request_body["task_ids"]:
            task = Task.query.get(task_id)
            task.goal_id = goal_id
            task_ids.append(task.task_id)
        
        db.session.commit()

        return {
            "id": goal.goal_id,
            "task_ids": task_ids
        }
            # new_task = Task(title=request_body["title"],
            #                 description=request_body["description"],
            #                 completed_at=request_body["completed_at"])

        db.session.add(new_task)
        #used when creating new record
        db.session.commit()
        #used when we change any of the records, we want to commit before returning, commit as soon as you expect the changes to persist in the database

        return make_response(f"Task {new_task.title} by {new_task.goal.name} successfully created", 201)