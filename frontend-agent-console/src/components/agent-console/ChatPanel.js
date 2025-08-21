import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import MessageBubble from './MessageBubble';
import AgentInput from './AgentInput';

const ChatPanel = () => {
    const [socket, setSocket] = useState(null);
    const [messages, setMessages] = useState([]);
    const [activeUsers, setActiveUsers] = useState([]);
    const [currentSender, setCurrentSender] = useState(null);

    const currentSenderRef = useRef(currentSender);
    const chatEndRef = useRef(null);

    // ✅ Redirect to login if agent not logged in
    useEffect(() => {
        const agentId = localStorage.getItem('agentId');
        if (!agentId) {
            window.location.href = "/login";
        }
    }, []);

    useEffect(() => {
        currentSenderRef.current = currentSender;
    }, [currentSender]);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages]);

    useEffect(() => {
        const agentId = localStorage.getItem('agentId');
        const newSocket = io('http://localhost:5001');
        setSocket(newSocket);

        newSocket.on('connect', () => {
            console.log('Connected to WebSocket as:', agentId);
            newSocket.emit('join_agent_console', { agent_id: agentId });
        });

        newSocket.on('new_user_message', (data) => {
            const { sender_id, message } = data;
            setActiveUsers((prev) => {
                if (!prev.includes(sender_id)) return [...prev, sender_id];
                return prev;
            });

            if (currentSenderRef.current === sender_id) {
                setMessages((prev) => [...prev, { from: 'user', message }]);
            }
        });

        newSocket.on('receive_message', (data) => {
            const { sender, text } = data;

            if (text === 'You are now connected to a live agent.') {
                alert('A user from the queue is now connected to you.');
                if (!currentSenderRef.current && activeUsers.length === 1) {
                    setCurrentSender(activeUsers[0]);
                }
            }

            if (currentSenderRef.current) {
                setMessages((prev) => [...prev, { from: sender, message: text }]);
            }
        });

        newSocket.on('end_chat', (data) => {
            if (data.sender_id === currentSenderRef.current) {
                setMessages((prev) => [
                    ...prev,
                    { from: 'system', message: 'The agent has ended the chat.' }
                ]);
            }
        });

        newSocket.on('user_connected_from_queue', (data) => {
            const sender_id = data.sender_id;
            alert(`New user assigned: ${sender_id}`);
            setActiveUsers((prev) => [...prev, sender_id]);
            setCurrentSender(sender_id);
            setMessages([]);
        });

        return () => {
            newSocket.disconnect();
        };
    }, []);

    // ✅ Logout handler
    const handleLogout = () => {
        const agentId = localStorage.getItem('agentId');
        if (socket) {
            socket.emit("logout_agent", { agent_id: agentId });
            socket.disconnect();
        }
        localStorage.removeItem("agentId");
        window.location.href = "/dashboard";
    };

    const sendAgentReply = (text) => {
        if (!currentSender) {
            alert('No active user selected');
            return;
        }

        fetch('http://localhost:5001/liveagent/agent_reply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender_id: currentSender, message: text }),
        });

        setMessages((prev) => [...prev, { from: 'agent', message: text }]);
    };

    const endChat = () => {
        if (!currentSender) {
            alert('No active user to end chat with');
            return;
        }

        if (socket) {
            socket.emit('end_chat_by_agent', { sender_id: currentSender });
        }

        setMessages((prev) => [...prev, { from: 'agent', message: 'You ended the chat.' }]);

        fetch('http://localhost:5001/liveagent/end_chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sender_id: currentSender }),
        });

        setActiveUsers((prev) => prev.filter((id) => id !== currentSender));
        setCurrentSender(null);
    };

    const handleUserSelect = (userId) => {
        setCurrentSender(userId);
        fetch(`http://localhost:5001/get_conversation_history/${userId}`)
            .then((res) => res.json())
            .then((data) => {
                const history = data.conversation.map((msg) => ({
                    from: msg.sender_type,
                    message: msg.message,
                }));
                setMessages(history);
            });
    };

    return (
        <div style={{ maxWidth: '900px', margin: '0 auto', padding: '20px' }}>
            {/* ✅ Logout Button */}
            <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: "10px" }}>
                <button
                    onClick={handleLogout}
                    style={{
                        backgroundColor: "red",
                        color: "white",
                        padding: "6px 12px",
                        borderRadius: "4px",
                        border: "none",
                        cursor: "pointer",
                    }}
                >
                    Logout
                </button>
            </div>

            <div style={{ marginBottom: '15px' }}>
                <strong>Active Users:</strong>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', marginTop: '8px' }}>
                    {activeUsers.map((userId, index) => (
                        <button
                            key={index}
                            onClick={() => handleUserSelect(userId)}
                            style={{
                                padding: '6px 12px',
                                backgroundColor: currentSender === userId ? '#4f46e5' : '#e0e0e0',
                                color: currentSender === userId ? 'white' : 'black',
                                border: 'none',
                                borderRadius: '4px',
                                cursor: 'pointer',
                            }}
                        >
                            {userId}
                        </button>
                    ))}
                </div>
            </div>

            <div
                style={{
                    border: '1px solid #ccc',
                    borderRadius: '6px',
                    padding: '10px',
                    height: '450px',
                    overflowY: 'auto',
                    backgroundColor: '#3d2a2aff',
                }}
            >
                {messages.map((msg, idx) => (
                    <MessageBubble key={idx} sender={msg.from} text={msg.message} />
                ))}
                <div ref={chatEndRef} />
            </div>

            <AgentInput onSend={sendAgentReply} onEndChat={endChat} />
        </div>
    );
};

export default ChatPanel;
