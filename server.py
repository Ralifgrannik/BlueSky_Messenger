import sqlite3
from flask import Flask, request
from flask_socketio import SocketIO, emit
from werkzeug.security import generate_password_hash, check_password_hash
from collections import defaultdict

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

online_users = {}                     # {username: {"sid": sid, "pub_key": pub_key}}
pending_messages = defaultdict(list)  # временное хранение только для оффлайн


def init_db():
    conn = sqlite3.connect('users.db')
    conn.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT)')
    conn.commit()
    conn.close()


@socketio.on('connect')
def handle_connect():
    print(f"[CONNECT] Новый клиент {request.sid}")


@socketio.on('disconnect')
def handle_disconnect():
    removed = [u for u, d in list(online_users.items()) if d['sid'] == request.sid]
    for u in removed:
        online_users.pop(u, None)
    if removed:
        emit('update_users', list(online_users.keys()), broadcast=True)


@socketio.on('register')
def handle_register(data):
    user = data.get('username')
    pw = data.get('password')
    if not user or not pw:
        return emit('auth_response', {'status': 'error', 'msg': 'Недостаточно данных'})

    hashed = generate_password_hash(pw)
    try:
        conn = sqlite3.connect('users.db')
        conn.execute('INSERT INTO users VALUES (?, ?)', (user, hashed))
        conn.commit()
        emit('auth_response', {'status': 'registered'})
    except sqlite3.IntegrityError:
        emit('auth_response', {'status': 'error', 'msg': 'Логин уже занят'})
    finally:
        conn.close()


@socketio.on('login')
def handle_login(data):
    user = data.get('username')
    pw = data.get('password')
    pub_key = data.get('pub_key')

    if not all([user, pw, pub_key]):
        return emit('auth_response', {'status': 'error', 'msg': 'Недостаточно данных'})

    conn = sqlite3.connect('users.db')
    res = conn.execute('SELECT password FROM users WHERE username = ?', (user,)).fetchone()
    conn.close()

    if res and check_password_hash(res[0], pw):
        online_users[user] = {"sid": request.sid, "pub_key": pub_key}
        print(f"[LOGIN] {user} вошёл успешно")

        emit('auth_response', {'status': 'success'})
        emit('update_users', list(online_users.keys()), broadcast=True)

        # Доставка оффлайн-сообщений
        if pending_messages[user]:
            print(f"[OFFLINE] Доставляем {len(pending_messages[user])} сообщений для {user}")
            for sender, payload in pending_messages[user]:
                emit('receive_msg', {'sender': sender, 'payload': payload}, to=request.sid)
            pending_messages[user].clear()
    else:
        emit('auth_response', {'status': 'error', 'msg': 'Неверный логин или пароль'})


@socketio.on('get_pub_key')
def get_key(data):
    target = data.get('target')
    if target in online_users:
        emit('target_key', {'pub_key': online_users[target]['pub_key']})
    else:
        emit('target_key', {'pub_key': None})


@socketio.on('private_msg')
def handle_private(data):
    sender = data.get('sender')
    target = data.get('target')
    payload = data.get('payload')

    if not sender or not target or payload is None:
        return

    print(f"[MSG] {sender} → {target} ({len(payload)} байт)")

    # 1. Получателю (если онлайн)
    if target in online_users:
        emit('receive_msg', {'sender': sender, 'payload': payload}, 
             to=online_users[target]['sid'])
    else:
        # 2. Сохраняем для оффлайн
        pending_messages[target].append((sender, payload))
        print(f"[PENDING] Сохранено для оффлайн {target}")

    # 3. отправляем отправителю, чтобы увидел сообщение
    if sender in online_users:
        emit('receive_msg', {'sender': sender, 'payload': payload}, 
             to=online_users[sender]['sid'])


@socketio.on('search_user')
def handle_search(data):
    query = (data.get('query') or '').strip()
    if not query:
        return emit('search_results', [])
    conn = sqlite3.connect('users.db')
    users = conn.execute("SELECT username FROM users WHERE username LIKE ? LIMIT 20",
                         ('%' + query + '%',)).fetchall()
    conn.close()
    emit('search_results', [u[0] for u in users])


if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)