from flask import Blueprint, jsonify, make_response, request
from app.models.task import Task
from app import db

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")


@tasks_bp.route("", methods=["POST"])
def create_task():
    request_body = request.get_json()
    new_task = Task(title = request_body["title"],
                    description = request_body["description"],
                    completed_at=request_body["completed_at"])

    db.session.add(new_task)
    db.session.commit()

    response_body = new_task.to_dict()

    return make_response(f"201 CREATED", 201)
    # return jsonify(response_body), 201

# @tasks_bp.route("", methods=["GET"])


# @books_bp.route("", methods=["GET"])
# def read_books():
#         books = Book.query.all()
#         books_response = []
#         for book in books:
#             books_response.append({
#                 "id": book.id,
#                 "title": book.title,
#                 "description": book.description
#             })
#         return jsonify(books_response)


# @books_bp.route("/<book_id>", methods=["PUT"])
# def update_book(book_id):
#     book = Book.query.get(book_id)
#     form_data = request.get_json()

#     book.title = form_data["title"]
#     book.description = form_data["description"]

#     db.session.commit()

#     return make_response(f"Book #{book.id} successfully updated")

# @tasks_bp.route("/<book_id>", methods=["DELETE"])
# def delete_book(book_id):
#     book = Book.query.get(book_id)

#     db.session.delete(book)
#     db.session.commit()
#     return make_response(f"Book #{book.id} successfully deleted")

