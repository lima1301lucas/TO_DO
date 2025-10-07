from flask import Blueprint, jsonify, request, session
from app.db import get_db_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data.get("login")
    senha = data.get("senha")

    if not login or not senha:
        return jsonify({"error": "E-mail ou Usuário e senha são obrigatórios!"}), 400

    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro na conexão ao banco"}), 500

    cursor = conn.cursor()

    try:
        if "@" in login:
            cursor.execute("SELECT id, username, senha, inativo FROM usuarios WHERE email = %s", (login,))
        else:
            cursor.execute("SELECT id, username, senha, inativo FROM usuarios WHERE username = %s", (login,))
        
        user = cursor.fetchone()

        if not user:
            return jsonify({"error": "Usuário não encontrado!"}), 404

        if user[3] == 1:
            return jsonify({"error": "Usuário inativo. Entre em contato com o suporte."}), 403

        if user[2] != senha:
            return jsonify({"error": "E-mail/Usuário ou senha incorretos."}), 401

        session['user_id'] = user[0]

        return jsonify({
            "message": "Login realizado com sucesso!",
            "user_id": user[0],
            "username": user[1]
        }), 200

    except Exception as e:
        return jsonify({"error": f"Erro ao efetuar login: {str(e)}"}), 500

    finally:
        cursor.close()
        conn.close()

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"message": "Logout realizado com sucesso!"}), 200