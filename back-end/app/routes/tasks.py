from flask import Blueprint, jsonify

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
def get_tasks():
    # Exemplo de retorno fixo
    tasks = [
        {"id": 1, "title": "Estudar Flask", "done": False},
        {"id": 2, "title": "Criar API To-Do", "done": True}
    ]
    return jsonify(tasks)