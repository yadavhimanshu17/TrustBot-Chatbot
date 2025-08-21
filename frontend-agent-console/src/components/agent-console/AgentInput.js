import React, { useState } from 'react';

const AgentInput = ({ onSend, onEndChat }) => {
    const [input, setInput] = useState('');

    const handleSend = () => {
        if (input.trim()) {
            onSend(input.trim());
            setInput('');
        }
    };

    return (
        <div style={{ marginTop: '12px', display: 'flex', gap: '10px' }}>
            <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Type your message..."
                style={{
                    flex: 1,
                    padding: '10px',
                    borderRadius: '6px',
                    border: '1px solid #ccc',
                }}
                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            />
            <button
                onClick={handleSend}
                style={{
                    padding: '10px 16px',
                    backgroundColor: '#4f46e5',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                }}
            >
                Send
            </button>
            <button
                onClick={onEndChat}
                style={{
                    padding: '10px 14px',
                    backgroundColor: '#dc3545',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                }}
            >
                End Chat
            </button>
        </div>
    );
};

export default AgentInput;
