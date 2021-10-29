from app import db
from app.models.task import Task
from app.models.goal import Goal
from flask import Blueprint, jsonify, make_response, request 

tasks_bp = Blueprint("tasks",__name__, url_prefix=("/tasks" ))

@tasks_bp.route("", methods=["GET", "POST"])
def handle_task():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []   
        for task in tasks:
                tasks_response.append(
                {
                    "id": task.task_id,
                    "title":task.title,
                    "description": task.description,
                    "is_complete": False if task.completed_at == None else True
                })    

        return jsonify(tasks_response)
        #return jsonify(tasks_response),200

    elif request.method == "POST":
        request_body = request.get_json()
        
        if "title" not in request_body or "description" not in request_body or "completed_at" not in request_body:
                    #return make_response("400 Bad Request",404)
                    return{
                        "details":"Invalid data"
                    },400


        new_task = Task(
        title=request_body["title"],
        description=request_body["description"],
        completed_at = request_body["completed_at"]
        )

        db.session.add(new_task)
        db.session.commit()

        return make_response(f"task {new_task.title} successfully created", 201)

 
@tasks_bp.route("/<task_id>",methods=["GET","PUT"])
def handle_task_get(task_id):
    task = Task.query.get(task_id)
    if task == None:
        return ("", 404)

    if request.method == "GET":
        return {
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description": task.description,
                "is_complete":False if task.completed_at == None else True
            }
        }
    if request.method == "PUT":
        form_data = request.get_json()

        task.title = form_data["title"]
        task.description = form_data["description"]

        db.session.commit()

        #return make_response(f"task #{task.id} successfully updated"),200
        return jsonify({
            "task":{
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":False if task.completed_at == None else True
            }

        })

    elif request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return {
                f"details":{task.description}("successfully deleted"),
        },400
                
#wave 2 - asc//desc sort    
@tasks_bp.route("/tasks?sort=asc", methods=["GET"])
def handle_task_asc():
    if request.method == "GET":
        tasks = Task.query.all()
        tasks_response = []
        task_asc_sort = sorted(tasks_response, key=lambda d: d['title'])   
        for task in tasks:
                tasks_response.append([
                {
                "id":task.task_id,
                "title":task.title,
                "description":task.description,
                "is_complete":False if task.completed_at == None else True
                }])   
        # task_asc_desc = sorted(tasks_response, key=itemgetter('name'), reverse=True)
        # #task_asc_sort = sorted(tasks_response, key=lambda d: d['title'])  

        return jsonify(task_asc_sort),200

#somehow need to sort the by title in desc 

#wave 3 