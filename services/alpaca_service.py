from flask import abort
from storages.alpaca_database import get_db_connection
from helpers.alpaca_helper import output_json_object
from sqlalchemy import create_engine


def create_alpaca(instruction, input_val, output):
    conn = get_db_connection()
    conn.execute('INSERT INTO alpacas (instruction, input, output) VALUES (?, ?, ?)',
                 (instruction, input_val, output))
    conn.commit()
    conn.close()
    return


def get_all_alpaca():
    conn = get_db_connection()
    alpacas = conn.execute('SELECT * FROM alpacas ORDER BY created DESC').fetchall()
    conn.close()
    return alpacas


def update_alpaca(instruction, input_val, output, alpaca_id):
    conn = get_db_connection()
    conn.execute('UPDATE alpacas SET instruction = ?, input = ?, output = ?'
                 ' WHERE id = ?',
                 (instruction, input_val, output, alpaca_id))
    conn.commit()
    conn.close()


def get_alpaca(alpaca_id):
    conn = get_db_connection()
    alpaca = conn.execute('SELECT * FROM alpacas WHERE id = ?',
                          (alpaca_id,)).fetchone()
    conn.close()
    if alpaca is None:
        abort(404)
    return alpaca


def delete_alpaca(alpaca_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM alpacas WHERE id = ?', (alpaca_id,))
    conn.commit()
    conn.close()


def export_data_to_json_file(user_info):
    engine = create_engine("sqlite:///instance/database.db")
    connection = engine.raw_connection()
    cursor = connection.cursor()
    if user_info.get('user_role') == 'admin':
        cursor.execute('SELECT * FROM alpaca')
    else:
        cursor.execute('SELECT * FROM alpaca WHERE created_by = ?', (user_info.get('user_id'),))

    col_names = [cn[0] for cn in cursor.description]

    json = ''
    json += "[\n"
    items = cursor.fetchall()
    for i, item in enumerate(items):
        if item == None:
            break
        json += '\t{\n'
        for j, col in enumerate(col_names):
            if col in ['id', 'created', 'created_by']:
                continue
            last = j == (len(col_names) - 1)
            json += output_json_object(col, item[j], last)

        if i != (len(items) - 1):
            # if i < 10000:
            json += '\t},\n'
        else:
            json += '\t}\n'

    json += "]"
    cursor.close()
    return json