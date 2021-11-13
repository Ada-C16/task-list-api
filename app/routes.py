from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import request, Blueprint, jsonify 
from datetime import datetime
import requests
import os


# class Task:
#     def __init__(self, id, title, description, completed_at = True):
#         self.id = id
#         self.title = title
#         self.description = description
#         self.completed_at = completed_at 



# tasks = [Task(1,"A Brand New Task", "Test Description", False )

tasks_bp = Blueprint("tasks_bp", __name__, url_prefix="/tasks") #functions that handles the endpoint
goals_bp = Blueprint("goals_bp", __name__, url_prefix="/goals")


@tasks_bp.route("", methods = ["POST", "GET"])
def handle_tasks():

#Wave 1 and Wave 2 

    if request.method == "POST":
        request_body = request.get_json() #request.get_json makes the text readable in json 
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
            return jsonify({"details":"Invalid data"}), 400
        
        new_task = Task(
            title= request_body["title"],
            description=request_body["description"],
            completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit()
        new_task_response = {"task":{
                "id": new_task.id,
                "title" : new_task.title,
                "description": new_task.description,
                "is_complete": False if new_task.completed_at == None else True 
                }
        }
        return jsonify(new_task_response), 201 
    

    if request.method == "GET":
        
        sort_query = request.args.get("sort") # create a variable called sort and assign request.args.get which gives me access to everything after the ? and everything after the question mark is a key value pair 
        tasks = Task.query.all()
        tasks_response = []
        for task in tasks:
                tasks_response.append(
                    {

                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True 


                    })
        
        if sort_query == "asc":
            # tasks = Task.query.order_by(Task.title.asc())
            tasks_response.sort(key=lambda x: x["title"])

        if sort_query == "desc" :
            tasks_response.sort(key=lambda x: x["title"], reverse=True)
            # .query.order_by("title".desc())
                
        # if sort_title_query:
        #     if sort_title_query == "asc":
        #         tasks = Task.query.order_by(Task.title.asc())
        #     elif sort_title_query == "desc":
        #         tasks = Task.query.order_by(Task.title.desc())
        return jsonify(tasks_response)
    
    

    
@tasks_bp.route("/<task_id>", methods = ["GET", "PUT", "DELETE"])
def handle_task(task_id): # cannot have the same handle 

    task = Task.query.get(task_id)# retrieve one task instance 
    if task is None:
        return jsonify(None), 404

    elif request.method == "GET":
        if not task.goal_id:
        
            return {"task":{
                    "id": task.id,
                    "title" : task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True 
                    }
            }, 200
        else:
            return {"task":{
                    "id": task.id,
                    "goal_id": task.goal.id,
                    "title" : task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True 
                    }
            }, 200

    
    elif request.method == "PUT":
        form_data = request.get_json() #this function takes the json data and turns it into a python dictionary
        print(form_data)
        task.title = form_data["title"]
        task.description = form_data["description"]
        db.session.commit()


        return {"task":{
                "id": task.id,
                "title" : task.title,
                "description": task.description,
                "is_complete": False if task.completed_at == None else True 
                }
        }, 200

    elif request.method == "DELETE": #deletes from DB
        db.session.delete(task) # deleting thee instance 
        db.session.commit()
        return jsonify({"details": f'Task {task.id} "{task.title}" successfully deleted'}), 200
        
#Wave 3 
@tasks_bp.route("/<task_id>/mark_incomplete", methods = ["PATCH"]) #because the endpoint prefix task is mention on line 18 the endpoint needs to start at/1
def handle_mark_incomplete(task_id): #because the url is referencing the task_id = 1, the handle function can remain empty but the task variable which holds Task.query.get(1) must have the same task_id value as endpoint
    
    task = Task.query.get(task_id) # Task stores the record of id 1, if id 1 doesn't exist what does it store? None 
    if task is None:
        return jsonify(None), 404
    else:
        task.completed_at = None
        db.session.commit()
        

        return {"task":{
                    "id": task.id,
                    "title" : task.title,
                    "description": task.description,
                    "is_complete": False 
                    }
            }, 200

def slack_bot(title):
    query_path = {"channel": "slack-api-test-channel", "text":title}
    header = {"Authorization": os.environ.get('BOT')}
    response = requests.post('https://slack.com/api/chat.postMessage', params = query_path, headers = header)
    print('Check to see if this works')
    return response.json()

@tasks_bp.route("/<task_id>/mark_complete", methods = ["PATCH"])
def handle_mark_complete(task_id):

    task = Task.query.get(task_id) 
    if task is None:
        return jsonify(None), 404
    else:
        task.completed_at = datetime.now()
        db.session.commit()
                    
        slack_bot(task.title)

        return jsonify( {"task":{
                    "id": task.id,
                    "title" : task.title,
                    "description": task.description,
                    "is_complete": True 
                    }
            }), 200
        

@goals_bp.route("", methods = ["POST", "GET"])
def handle_goals():

    if request.method == "GET":

        goals = Goal.query.all()

        each_goal = []
        
        for goal in goals:

            each_goal.append({ "id": goal.id,
                    "title": goal.title}), 200

        return jsonify (each_goal)

    elif request.method == "POST":

        
        request_body = request.get_json() #request.get_json makes the text readable in json 
        if "title" not in request_body:
            return jsonify({"details":"Invalid data"}), 400
        
        new_goal = Goal(
            title= request_body["title"]) #new instance 

        db.session.add(new_goal)
        db.session.commit()
        new_goal_response = {"goal":{
                "id": new_goal.id,
                "title" : new_goal.title}}

        return jsonify(new_goal_response), 201
                
        


#Wave 5 
@goals_bp.route("/<goal_id>", methods = [ "GET", "DELETE", "PUT"])
def handle_one_goal(goal_id):

    goal = Goal.query.get(goal_id)

    if goal is None:
            return jsonify(None), 404
    elif request.method == "GET":


            return ( { "goal": {
                    "id": goal.id,
                    "title": goal.title

            }}), 200

    

    elif request.method == "PUT":
        if goal.title == None:
            return None, 404
        form_data = request.get_json() #this function takes the json data and turns it into a python dictionary
        goal.title = form_data["title"]
        db.session.commit()

        return ( { "goal": {
                    "id": goal.id,
                    "title": goal.title

            }}),200


    elif request.method == "DELETE":


        db.session.delete(goal)
        db.session.commit()
        
        return {"details": f'Goal {goal_id} \"{goal.title}\" successfully deleted'}, 200

@goals_bp.route("/<goal_id>/tasks", methods = [ "GET", "POST"])
def handle_goals_and_tasks(goal_id):

    goal = Goal.query.get(goal_id)
    

    if goal is None:
        return jsonify(None), 404

    if request.method == "POST":
        request_body = request.get_json()

        for task_id in request_body["task_ids"]: 
            task = Task.query.get(task_id)
            if task is None:
                return jsonify (None), 404
            
            goal.tasks.append(task)
    
        
        db.session.commit()
        task_ids =[]
        for one_task in goal.tasks:
            task_ids.append(one_task.id)

        return jsonify({"id": goal.id,"task_ids": task_ids })

    elif request.method == "GET":
        request_body = request.get_json()

        task_in_goals = []

        for task in goal.tasks:
            task_in_goals.append({"id":task.id,"goal_id":task.goal_id, "title":task.title,"description":task.description, "is_complete":bool(task.completed_at)})

        return jsonify ({"id":goal.id, "title":goal.title, "tasks": task_in_goals}), 200

        

    

        
    
    



    



