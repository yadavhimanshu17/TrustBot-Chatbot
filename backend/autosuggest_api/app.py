# === Flask and WebSocket Imports ===
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import mysql.connector

# === Flask App Initialization ===
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# === MySQL Database Connection ===
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2378",
    database="rasa_chatbot"
)
cursor = db.cursor()

# === Live Agent State ===
available_agents = set()
agent_user_mapping = {}
user_queue = []
active_sessions = {}

# === Static Suggestions ===
SUGGESTIONS = [
    "Explore Services", "WhatsApp Service", "SMS Service", "Email Service", "Chatbot Service",
    "Request Demo", "Contact Support", "Contact Sales", "Pricing Info",
    "WhatsApp Pricing", "SMS Pricing", "Email Pricing", "Chatbot Pricing"
]

RASA_URL = "http://localhost:5005"

# === Save Message to DB ===
def save_message(sender_id, sender_type, message):
    sql = "INSERT INTO live_agent_data (sender_id, sender_type, message) VALUES (%s, %s, %s)"
    cursor.execute(sql, (sender_id, sender_type, message))
    db.commit()

# === WebSocket Events ===
@socketio.on('connect')
def handle_connect():
    emit("connection_status", {"status": "Connected to Live Agent Server"})
    print(f"Frontend connected via WebSocket: {request.sid}")

@socketio.on('join_agent_console')
def join_agent_console(data):
    agent_id = data.get('agent_id')
    print(f"[AGENT JOIN] Agent ID: {agent_id} | Socket ID: {request.sid}")
    available_agents.add(request.sid)
    join_room('agents')
    assign_user_to_agent()

@socketio.on('logout_agent')
def logout_agent(data):
    agent_id = data.get('agent_id')
    print(f"[AGENT LOGOUT] Agent ID: {agent_id} | Socket ID: {request.sid}")

    if request.sid in available_agents:
        available_agents.remove(request.sid)
    if request.sid in agent_user_mapping:
        del agent_user_mapping[request.sid]

    emit("agent_logout_ack", {"status": "logged_out"}, room=request.sid)

@socketio.on('send_message')
def handle_send_message(data):
    sender_id = data.get('sender_id')
    message = data.get('text')

    if not sender_id:
        return

    if sender_id not in active_sessions:
        active_sessions[sender_id] = {'socket_id': request.sid, 'handover': False, 'waiting': False}
    else:
        active_sessions[sender_id]['socket_id'] = request.sid

    join_room(sender_id)
    emit('typing_start', {'status': True}, room=request.sid)

    if message.lower() == 'connect to live agent':
        if available_agents:
            agent_sid = available_agents.pop()
            agent_user_mapping[agent_sid] = sender_id
            active_sessions[sender_id]['handover'] = True
            active_sessions[sender_id]['waiting'] = False
            emit('receive_message', {'sender': 'bot', 'text': 'Connecting you to a live agent...'}, room=request.sid)
            socketio.emit('user_connected_from_queue', {'sender_id': sender_id}, room=agent_sid)
        else:
            if sender_id not in user_queue:
                user_queue.append(sender_id)
                active_sessions[sender_id]['handover'] = False
                active_sessions[sender_id]['waiting'] = True
            emit('receive_message', {'sender': 'bot', 'text': 'All agents are busy. You are in queue.'}, room=request.sid)

        emit('typing_end', {'status': False}, room=request.sid)
        return

    if active_sessions[sender_id]['handover'] and not active_sessions[sender_id]['waiting']:
        agent_sid = next((sid for sid, user in agent_user_mapping.items() if user == sender_id), None)
        if agent_sid:
            socketio.emit('new_user_message', {'sender_id': sender_id, 'message': message}, room=agent_sid)
            save_message(sender_id, 'user', message)
    else:
        response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json={"sender": sender_id, "message": message})
        for msg in response.json():
            emit('receive_message', {
                'sender': 'bot',
                'text': msg.get('text', ''),
                'buttons': msg.get('buttons', []),
                'custom': msg.get('custom', {})   # <-- forward custom (carousel will be here)
            }, room=request.sid)

    emit('typing_end', {'status': False}, room=request.sid)

# === Agent Reply (called via API from Agent Panel) ===
@app.route("/liveagent/agent_reply", methods=["POST"])
def agent_reply():
    data = request.json
    sender_id = data.get("sender_id")
    message = data.get("message")

    if sender_id in active_sessions:
        user_sid = active_sessions[sender_id]['socket_id']
        socketio.emit('receive_message', {'sender': 'agent', 'text': message}, room=sender_id)
        save_message(sender_id, 'agent', message)
        return jsonify({"status": "agent_message_sent"}), 200
    return jsonify({"error": "Sender ID not active"}), 404

# === End Chat from Agent Panel ===
@app.route("/liveagent/end_chat", methods=["POST"])
def end_live_agent_chat():
    data = request.json
    sender_id = data.get("sender_id")

    if sender_id in active_sessions:
        active_sessions[sender_id]['handover'] = False
        active_sessions[sender_id]['waiting'] = False

        agent_sid = next((sid for sid, user in agent_user_mapping.items() if user == sender_id), None)

        if agent_sid:
            available_agents.add(agent_sid)
            del agent_user_mapping[agent_sid]

        socketio.emit('receive_message', {'sender': 'bot', 'text': 'Live agent session ended. Resuming bot...'}, room=sender_id)

        response = requests.post(f"{RASA_URL}/webhooks/rest/webhook", json={"sender": sender_id, "message": "end live agent chat"})
        for msg in response.json():
            socketio.emit('receive_message', {
                'sender': 'bot',
                'text': msg.get('text', ''),
                'buttons': msg.get('buttons', []),
                'custom': msg.get('custom', {})
            }, room=sender_id)

        assign_user_to_agent()
        return jsonify({"status": "chat_ended"}), 200

    return jsonify({"error": "Sender ID not active"}), 404

# === Assign Users from Queue to Free Agents ===
def assign_user_to_agent():
    while available_agents and user_queue:
        agent_sid = available_agents.pop()
        sender_id = user_queue.pop(0)
        agent_user_mapping[agent_sid] = sender_id
        active_sessions[sender_id]['handover'] = True
        active_sessions[sender_id]['waiting'] = False
        socketio.emit('receive_message', {'sender': 'bot', 'text': 'You are now connected to a live agent.'}, room=sender_id)
        socketio.emit('user_connected_from_queue', {'sender_id': sender_id}, room=agent_sid)

# === Suggestion Endpoint ===
@app.route('/suggest', methods=['POST', 'OPTIONS'])
def suggest():
    if request.method == 'OPTIONS':
        return jsonify({'status': 'OK'}), 200
    data = request.get_json()
    query = data.get('query', '').lower()
    matched_suggestions = [s for s in SUGGESTIONS if s.lower().startswith(query)] if query else []
    return jsonify({'suggestions': matched_suggestions})

# === Conversation History API ===
@app.route('/get_conversation_history/<sender_id>', methods=['GET'])
def get_conversation_history(sender_id):
    cursor.execute("""
        SELECT sender_type, message, timestamp 
        FROM live_agent_data 
        WHERE sender_id = %s 
        AND sender_type IN ('user', 'agent')
        ORDER BY timestamp ASC
    """, (sender_id,))
    rows = cursor.fetchall()
    history = []
    for row in rows:
        history.append({
            'sender_type': row[0],
            'message': row[1],
            'timestamp': row[2].strftime('%Y-%m-%d %H:%M:%S') if row[2] else ''
        })
    return jsonify({'conversation': history}), 200

# === Admin APIs ===
@app.route("/admin/get_agents", methods=["GET"])
def get_agents():
    cursor.execute("SELECT agent_id, agent_name, email FROM agent_login_details")
    agents = cursor.fetchall()
    return jsonify([{"agent_id": a[0], "agent_name": a[1], "email": a[2]} for a in agents]), 200

@app.route("/admin/add_agent", methods=["POST"])
def add_agent():
    data = request.json
    agent_id = data.get("agent_id")
    agent_name = data.get("agent_name")
    email = data.get("email")
    password = data.get("password")
    hashed_password = generate_password_hash(password)
    try:
        cursor.execute(
            "INSERT INTO agent_login_details (agent_id, agent_name, email, password) VALUES (%s, %s, %s, %s)",
            (agent_id, agent_name, email, hashed_password)
        )
        db.commit()
        return jsonify({"status": "success", "message": "Agent added."}), 200
    except mysql.connector.Error as err:
        return jsonify({"status": "fail", "message": str(err)}), 400

@app.route("/admin/update_agent/<agent_id>", methods=["PUT"])
def update_agent(agent_id):
    data = request.json
    cursor.execute(
        "UPDATE agent_login_details SET agent_name = %s, email = %s WHERE agent_id = %s",
        (data.get("agent_name"), data.get("email"), agent_id)
    )
    db.commit()
    return jsonify({"status": "success", "message": "Agent updated."}), 200

@app.route("/admin/delete_agent/<agent_id>", methods=["DELETE"])
def delete_agent(agent_id):
    cursor.execute("DELETE FROM agent_login_details WHERE agent_id = %s", (agent_id,))
    db.commit()
    return jsonify({"status": "success", "message": "Agent deleted."}), 200

@app.route("/agent_login", methods=["POST"])
def agent_login():
    data = request.json
    agent_id = data.get("agent_id")
    password = data.get("password")
    
    cursor.execute("SELECT password, is_admin FROM agent_login_details WHERE agent_id = %s", (agent_id,))
    result = cursor.fetchone()

    if result and check_password_hash(result[0], password):
        return jsonify({
            "status": "success",
            "agent_id": agent_id,
            "is_admin": result[1]  # 1 or 0
        }), 200

    return jsonify({"status": "fail", "message": "Invalid credentials"}), 401

# === App Entry Point ===
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)
