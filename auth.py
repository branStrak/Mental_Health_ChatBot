from flask import Blueprint, request, jsonify, session
import psycopg2
from psycopg2 import Error
from werkzeug.security import generate_password_hash, check_password_hash

import os

auth_bp = Blueprint('auth', __name__)

DB_CONFIG = {
    'dbname': 'MentalHealthDB',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    try:
        database_url = os.environ.get('DATABASE_URL')
        if database_url:
            connection = psycopg2.connect(database_url)
        else:
            connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

@auth_bp.route('/register', methods=['POST'])
def api_register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    age = data.get('age')
    password = data.get('password')
    gender = data.get('gender')
    if gender:
        gender = gender.capitalize()

    if not all([username, email, password]):
        return jsonify({'error': 'Username, email, and password are required'}), 400

    password_hash = generate_password_hash(password)

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash, age, gender, created_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (email) DO NOTHING
                RETURNING user_id
                """,
                (username, email, password_hash, age, gender)
            )
            result = cursor.fetchone()
            connection.commit()
            if result:
                cursor=connection.cursor()
                cursor.execute("""
                SELECT user_id FROM users WHERE email = %s
                """,
                (email,))
                result=cursor.fetchone()
                user_id=result[0] if result else None

                return jsonify({'message': 'Registration successful', 'user_id': user_id}), 201
            else:
                return jsonify({'error': 'Email already registered'}), 409
        except Error as e:
            connection.rollback()
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Database connection failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({'error': 'Email and password are required'}), 400

    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT user_id, password_hash FROM users WHERE email = %s
                """,
                (email,)
            )
            result = cursor.fetchone()
            if result:
                user_id, stored_password_hash = result
                if check_password_hash(stored_password_hash, password):
                    return jsonify({'message': 'Login successful', 'user_id': user_id}), 200
                else:
                    return jsonify({'error': 'Invalid password'}), 401
            else:
                return jsonify({'error': 'Email not found'}), 404
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            cursor.close()
            connection.close()
    return jsonify({'error': 'Database connection failed'}), 500