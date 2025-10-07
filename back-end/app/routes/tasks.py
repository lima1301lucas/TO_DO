from flask import Blueprint, Response, jsonify, request
from collections import defaultdict
from app.db import get_db_connection
import MySQLdb, json

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/<int:user_id>', methods=['GET'])
def get_tasks(user_id):

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor(MySQLdb.cursors.DictCursor)

    try:
        cursor.execute("""
            SELECT 
                t.id,
                t.title,
                t.description,
                t.created_at,
                t.end_at,
                t.concluido,
                p.name AS prioridade,
                c.name AS categoria
            FROM tarefas t
            JOIN prioridades p ON t.priority_id = p.id
            JOIN categorias c ON t.category_id = c.id
            WHERE t.user_id = %s AND t.end_at >= CURDATE()
            ORDER BY t.end_at ASC;
        """, (user_id,))

        tasks_data = cursor.fetchall()

        if not tasks_data:
            return jsonify({"error": "Nenhuma tarefa encontrada"}), 404

        tasks_grouped = defaultdict(list)

        for task in tasks_data:
            created = task["created_at"].strftime("%Y-%m-%d") if task["created_at"] else None
            end = task["end_at"].strftime("%Y-%m-%d") if task["end_at"] else None
            date_key = end 

            tasks_grouped[date_key].append({
                "id": task["id"],
                "titulo": task["title"],
                "descricao": task["description"],
                "criada_em": created,
                "data_final": end,
                "prioridade": task["prioridade"],
                "categoria": task["categoria"],
                "concluido": bool(task["concluido"])
            })

        return Response(json.dumps(tasks_grouped, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8"), 200

    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('<int:user_id>/<int:task_id>', methods=['GET'])
def get_task_by_id(user_id, task_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor(MySQLdb.cursors.DictCursor)
    
    try:
        cursor.execute("""
            SELECT 
                t.id,
                t.title,
                t.description,
                t.created_at,
                t.end_at,
                p.name AS prioridade,
                c.name AS categoria,
                t.concluido
            FROM tarefas t
            JOIN prioridades p ON t.priority_id = p.id
            JOIN categorias c ON t.category_id = c.id
            WHERE t.id = %s AND t.user_id = %s;
        """, (task_id, user_id))

        task = cursor.fetchone()
        task["created_at"] = task["created_at"].strftime("%d/%m/%Y") if task["created_at"] else None
        task["end_at"] = task["end_at"].strftime("%d/%m/%Y") if task["end_at"] else None
        if not task:
            return jsonify({"error": "Tarefa não encontrada!"}), 404

        return Response(json.dumps(task, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8"), 200

    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/insert/', methods=['POST'])
def create_task():
    data = request.json
    title = data.get('title')
    description = data.get('description')
    end_at = data.get('end_at')
    user_id = data.get('user_id')
    priority_id = data.get('priority_id')
    category_id = data.get('category_id')

    if not all([title, description, end_at, user_id, priority_id, category_id]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO tarefas (title, description, end_at, user_id, priority_id, category_id)
            VALUES (%s, %s, %s, %s, %s, %s);
        """, (title, description, end_at, user_id, priority_id, category_id))
        conn.commit()

        return jsonify({"message": "Tarefa criada com sucesso!"}), 201

    except Exception as e:
        return jsonify({"error": f"Erro ao criar tarefa: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/upadate/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    title = data.get('title')
    description = data.get('description')
    end_at = data.get('end_at')
    priority_id = data.get('priority_id')
    category_id = data.get('category_id')

    if not all([title, description, end_at, priority_id, category_id]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM tarefas WHERE id = %s;", (task_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Tarefa não encontrada!"}), 404

        cursor.execute("""
            UPDATE tarefas
            SET title = %s, description = %s, end_at = %s, 
                priority_id = %s, category_id = %s
            WHERE id = %s;
        """, (title, description, end_at, priority_id, category_id, task_id))
        conn.commit()

        return jsonify({"message": "Tarefa atualizada com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar tarefa: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

@tasks_bp.route('/changeStatus/<int:task_id>', methods=['PUT'])
def complete_task(task_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM tarefas WHERE id = %s;", (task_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Tarefa não encontrada!"}), 404

        cursor.execute("UPDATE tarefas SET concluido = TRUE WHERE id = %s;", (task_id,))
        conn.commit()

        return jsonify({"message": "Status da tarefa com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao mudar status tarefa: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


@tasks_bp.route('/delete/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM tarefas WHERE id = %s;", (task_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Tarefa não encontrada!"}), 404

        cursor.execute("DELETE FROM tarefas WHERE id = %s;", (task_id,))
        conn.commit()

        return jsonify({"message": "Tarefa deletada com sucesso!"}), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao deletar tarefa: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()