import React, { useState } from 'react';
import axios from 'axios';

const ChatHistoryViewer = ({ onFetchComplete }) => {
    const [senderId, setSenderId] = useState('');
    const [conversation, setConversation] = useState([]);
    const [loading, setLoading] = useState(false);

    const fetchConversation = async () => {
        if (!senderId.trim()) return;
        setLoading(true);
        try {
            const res = await axios.get(`http://localhost:5001/get_conversation_history/${senderId}`);
            setConversation(res.data.conversation);

            // Clear ChatbotContainer Input
            if (onFetchComplete) {
                onFetchComplete();
            }

            // Clear SenderId Input)
            setSenderId('');

        } catch (error) {
            console.error('Error fetching conversation:', error);
        }
        setLoading(false);
    };

    return (
        <div className="p-6 bg-white shadow-md rounded-md mb-6">
            <h2 className="text-xl font-semibold mb-4">Chat History Viewer</h2>
            <div className="flex mb-4">
                <input
                    type="text"
                    value={senderId}
                    onChange={(e) => setSenderId(e.target.value)}
                    placeholder="Enter Sender ID"
                    className="border px-3 py-2 rounded-md mr-2 w-64"
                />
                <button
                    onClick={fetchConversation}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                    {loading ? 'Loading...' : 'Fetch'}
                </button>
            </div>

            <div className="space-y-3 max-h-96 overflow-y-auto">
                {conversation.map((msg, index) => (
                    <div
                        key={index}
                        className={`p-3 rounded-lg ${msg.sender_type === 'user' ? 'bg-gray-100 text-left' :
                            msg.sender_type === 'agent' ? 'bg-green-100 text-right' : ''
                            }`}
                    >
                        <div className="text-sm">{msg.message}</div>
                        <div className="text-xs text-gray-500">{new Date(msg.timestamp).toLocaleString()}</div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ChatHistoryViewer;
