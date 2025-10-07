from flask import Blueprint, Response, jsonify, request
from app.db import get_db_connection
import json

users_bp = Blueprint('users', __name__)

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500
    
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, username, nome, sobrenome, email FROM usuarios WHERE id = %s",(user_id,))
        user_data = cursor.fetchone()

        if not user_data:
            return jsonify({"error": "Usuário não encontrado"}), 404
        
        user= {
            "id": user_data[0],
            "username": user_data[1],
            "nome": user_data[2],
            "sobrenome": user_data[3],
            "email": user_data[4]
        }
        
        return Response(json.dumps(user, ensure_ascii=False, indent=2), content_type="application/json; charset=utf-8"), 200

    finally:
        cursor.close()
        conn.close()


@users_bp.route('/create/', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    nome = data.get("nome")
    sobrenome = data.get("sobrenome")
    email = data.get("email")
    senha = data.get("senha")

    if not all([username, nome, sobrenome, email, senha]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE username = %s OR email = %s", (username, email))
        if cursor.fetchone():
            return jsonify({"error": "Usuário ou e-mail já cadastrado!"}), 409
        
        cursor.execute( "INSERT INTO usuarios (username, nome, sobrenome, email, senha, inativo) VALUES (%s, %s, %s, %s, %s, 0)", (username, nome, sobrenome, email, senha))
        conn.commit()
        user_id = cursor.lastrowid

        return jsonify({
            "message": "Usuário criado com sucesso!",
            "user_id": user_id,
            "username": username,
            "nome": nome,
            "sobrenome": sobrenome,
            "email": email
        }), 201

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao criar usuário: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route('/update/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    username = data.get("username")
    nome = data.get("nome")
    sobrenome = data.get("sobrenome")
    email = data.get("email")
    senha = data.get("senha")

    if not all([username, nome, sobrenome, email, senha]):
        return jsonify({"error": "Todos os campos são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            return jsonify({"error": "Usuário não encontrado!"}), 404

        cursor.execute("SELECT id FROM usuarios WHERE (username = %s OR email = %s) AND id != %s", (username, email, user_id))
        if cursor.fetchone():
            return jsonify({"error": "Usuário ou e-mail já cadastrado!"}), 409

        cursor.execute("UPDATE usuarios SET username = %s, nome = %s, sobrenome = %s, email = %s, senha = %s WHERE id = %s", (username, nome, sobrenome, email, senha, user_id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Nenhuma alteração foi feita."}), 200

        return jsonify({
            "message": "Usuário atualizado com sucesso!",
            "username": username,
            "nome": nome,
            "sobrenome": sobrenome,
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao atualizar usuário: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route('/changePassword/', methods=['PUT'])
def change_password():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    nova_senha = data.get("nova_senha")

    if not all([username, email, nova_senha]):
        return jsonify({"error": "Usuário, e-mail e nova senha são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, senha FROM usuarios WHERE username = %s AND email = %s AND inativo = 0 ", (username, email))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Usuário não encontrado ou inativo!"}), 404

        if user[1] == nova_senha:
            return jsonify({"error": "A nova senha deve ser diferente das anteriores."}), 400

        cursor.execute("UPDATE usuarios SET senha = %s WHERE id = %s", (nova_senha, user[0]))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"message": "Nenhuma alteração foi feita."}), 200

        return jsonify({
            "message": "Senha alterada com sucesso!",
            "username": username,
            "email": email
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao alterar senha: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route('/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão com o banco"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT inativo FROM usuarios WHERE id = %s", (user_id,))
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": f"Usuário não encontrado!"}), 404
        
        if user[0] == 1:
            return jsonify({"message": "Usuário já está inativo."}), 200

        cursor.execute("UPDATE usuarios SET inativo = 1 WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({
            "message": f"Usuário {user_id} inativado com sucesso!"
        }), 200

    except Exception as e:
        conn.rollback()
        return jsonify({"error": f"Erro ao inativar usuário: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()