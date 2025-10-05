from flask import Blueprint, jsonify, request, session
from app.db import get_db_connection

users_bp = Blueprint('users', __name__)

@users_bp.route('/', methods=['GET'])
def get_users():
    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, username, nome, sobrenome, email FROM todo_app.usuarios;")
        users_data = cursor.fetchall()

        if not users_data:
            return jsonify({"error": "Usuários não encontrados"}), 404
        
        users_list = []
        for user in users_data:
            user_dict = {
                "id": user[0],
                "username": user[1],
                "nome": user[2],
                "sobrenome": user[3],
                "email": user[4]
            }
            users_list.append(user_dict)

        return jsonify(users_list)

    finally:
        cursor.close()
        conn.close()

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

        return jsonify(user)

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    nome = data.get("nome")
    sobrenome = data.get("sobrenome")
    email = data.get("email")
    senha = data.get("senha")

    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500
    
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO usuarios (username, nome, sobrenome, email, senha, inativo) VALUES (%s, %s, %s, %s, %s, %s)", (username, nome, sobrenome, email, senha, 1))
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

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    data = request.json
    username = data.get("username")
    nome = data.get("nome")
    sobrenome = data.get("sobrenome")
    email = data.get("email")
    senha = data.get("senha")

    conn = get_db_connection()

    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500
    
    cursor = conn.cursor()

    try:
        cursor.execute("UPDATE usuarios SET username = %s, nome = %s, sobrenome = %s, email = %s, senha = %s WHERE id = %s", (username, nome, sobrenome, email, senha, user_id))
        conn.commit()

        return jsonify({
            "message": "Usuário atualizado com sucesso!",
            "username": username,
            "nome": nome,
            "sobrenome": sobrenome,
            "email": email
        }), 200

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão com o banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE usuarios SET inativo = 1 WHERE id = %s", (user_id,))
        conn.commit()

        return jsonify({
            "message": f"Usuário {user_id} deletado com sucesso!"
        }), 200

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get("email")
    senha = data.get("senha")

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, username, senha FROM usuarios WHERE email = %s AND inativo = 0", (email,))
        user = cursor.fetchone()

        if not user or user[2] != senha:
            return jsonify({"error": "Email ou senha incorretos"}), 401

        session['user_id'] = user[0]

        return jsonify({
            "message": "Login realizado com sucesso!",
            "user_id": user[0],
            "username": user[1]
        }), 200

    finally:
        cursor.close()
        conn.close()

@users_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout realizado com sucesso!"}), 200