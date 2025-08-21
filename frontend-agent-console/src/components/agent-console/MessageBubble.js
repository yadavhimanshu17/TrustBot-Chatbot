import React from 'react';

const MessageBubble = ({ sender, text }) => {
    const isAgent = sender === 'agent';
    return (
        <div
            style={{
                display: 'flex',
                justifyContent: isAgent ? 'flex-end' : 'flex-start',
                margin: '5px 0',
            }}
        >
            <div
                style={{
                    backgroundColor: isAgent ? '#d1e7dd' : '#f8d7da',
                    color: '#333',
                    padding: '10px 14px',
                    borderRadius: '16px',
                    maxWidth: '70%',
                    boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
                }}
            >
                <strong>{isAgent ? 'Agent' : 'User'}: </strong>
                {text}
            </div>
        </div>
    );
};

export default MessageBubble;
