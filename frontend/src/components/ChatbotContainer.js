import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import ChatWindow from './ChatWindow';
import { SendHorizontal } from 'lucide-react';
import axios from 'axios';
import io from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';  // Unique User ID

const ChatbotContainer = forwardRef((props, ref) => {
    const [isOpen, setIsOpen] = useState(false);
    const [isExpanded, setIsExpanded] = useState(false);
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [isRefreshing, setIsRefreshing] = useState(false);
    const [isTyping, setIsTyping] = useState(false);
    const [isTemporarilyHidden, setIsTemporarilyHidden] = useState(false);
    const [isFeedbackSending, setIsFeedbackSending] = useState(false);
    const chatEndRef = useRef(null);
    const inputRef = useRef(null);
    const debounceTimer = useRef(null);
    const socket = useRef(null);
    const [senderId] = useState(() => uuidv4());

    // Expose method to parent (clearInputBox)
    useImperativeHandle(ref, () => ({
        clearInputBox() {
            setInput('');
            setSuggestions([]);
        }
    }));

    useEffect(() => {
        socket.current = io('http://localhost:5001');

        socket.current.on('receive_message', (data) => {
            console.log('[Socket] Received:', data);
            setIsTyping(false);

            const newMsg = {
                id: Date.now() + Math.random(),
                sender: data.sender,
                text: data.text,
                timestamp: new Date(),
                buttons: data.buttons ? data.buttons.map(btn => ({ ...btn, disabled: false })) : [],
                carousel: data.custom && data.custom.carousel ? data.custom.carousel : null
            };
            setMessages(prev => [...prev, newMsg]);
        });

        socket.current.on('connection_status', (data) => {
            console.log('[Socket] Status:', data.status);
        });

        return () => {
            socket.current.disconnect();
        };
    }, []);

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isTyping]);

    useEffect(() => {
        if (isOpen && inputRef.current) {
            inputRef.current.focus();
        }
    }, [isOpen, isExpanded]);

    const sendMessageToRasa = async (message) => {
        try {
            setIsTyping(true);
            const res = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
                sender: senderId,
                message: message
            });

            res.data.forEach(msg => {
                const botMsg = {
                    id: Date.now() + Math.random(),
                    sender: 'bot',
                    text: msg.text || '',
                    timestamp: new Date(),
                    buttons: msg.buttons ? msg.buttons.map(btn => ({ ...btn, disabled: false })) : [],
                    carousel: msg.custom && msg.custom.carousel ? msg.custom.carousel : null
                };
                setMessages(prev => [...prev, botMsg]);
            });
        } catch (error) {
            console.error('Error sending message to Rasa:', error);
        } finally {
            setIsTyping(false);
        }
    };

    const handleSend = () => {
        if (!input.trim()) return;

        const userMsg = { sender: 'user', text: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setSuggestions([]);
        setIsTyping(true);

        // Emit to Server for Live Agent / Rasa flow
        socket.current.emit('send_message', { sender_id: senderId, text: input });
    };

    const handleQuickReply = (title, payload, disableIndex, type) => {
        // Disable clicked button
        setMessages(prevMessages => prevMessages.map((msg, idx) => {
            if (idx === disableIndex) {
                return {
                    ...msg,
                    buttons: msg.buttons.map(btn =>
                        btn.title === title ? { ...btn, disabled: true } : btn
                    )
                };
            }
            return msg;
        }));

        // Show bubble only if not postback
        if (type !== 'postback') {
            const userMsg = { sender: 'user', text: title, timestamp: new Date() };
            setMessages(prev => [...prev, userMsg]);
        }

        setIsTyping(true);
        socket.current.emit('send_message', { sender_id: senderId, text: payload });
    };

    const handleFeedbackSubmit = async (messageId, feedbackType, feedbackText) => {
        const payload = `/give_feedback{"message_id": "${messageId}", "feedback_type": "${feedbackType}", "feedback_text": "${feedbackText}"}`;
        setIsFeedbackSending(true);
        try {
            const res = await axios.post('http://localhost:5005/webhooks/rest/webhook', {
                sender: senderId,
                message: payload
            });

            res.data.forEach(msg => {
                const botMsg = {
                    id: Date.now() + Math.random(),
                    sender: 'bot',
                    text: msg.text || '',
                    timestamp: new Date(),
                    buttons: msg.buttons ? msg.buttons.map(btn => ({ ...btn, disabled: false })) : [],
                };
                setMessages(prev => [...prev, botMsg]);
            });

        } catch (error) {
            console.error("Error sending feedback:", error);
        } finally {
            setIsFeedbackSending(false);
        }
    };

    const fetchSuggestions = async (query) => {
        try {
            const res = await axios.post('http://localhost:5001/suggest', { query });
            if (res.data && res.data.suggestions) {
                setSuggestions(res.data.suggestions);
            }
        } catch (error) {
            console.error('Error fetching suggestions:', error);
        }
    };

    const handleInputChange = (e) => {
        const value = e.target.value;
        setInput(value);

        clearTimeout(debounceTimer.current);
        if (value.trim()) {
            debounceTimer.current = setTimeout(() => {
                fetchSuggestions(value);
            }, 300);
        } else {
            setSuggestions([]);
        }
    };

    const handleSuggestionClick = (suggestion) => {
        setInput(suggestion);
        setSuggestions([]);
        handleSend();
    };

    const handleToggleChat = () => {
        setIsOpen(prev => !prev);
        if (!isOpen && messages.length === 0) {
            sendMessageToRasa('/main_menu');
        }
    };

    const toggleExpand = () => {
        setIsExpanded(!isExpanded);
    };

    const handleExitClick = () => {
        setIsOpen(false);
    };

    const handleRefreshChat = async () => {
        setIsRefreshing(true);
        setMessages([]);
        await sendMessageToRasa('/main_menu');
        setIsRefreshing(false);
    };

    const handleTemporaryHide = () => {
        setIsTemporarilyHidden(true);
        setTimeout(() => {
            setIsTemporarilyHidden(false);
        }, 30000);
    };

    return (
        <div className="absolute bottom-5 right-5">
            {!isOpen && !isTemporarilyHidden && (
                <div className="fixed bottom-5 right-5 flex items-center space-x-2">
                    <div
                        onClick={handleToggleChat}
                        className="bg-white border border-gray-300 rounded-full flex items-center shadow-lg pl-3 pr-4 py-2 space-x-2 cursor-pointer hover:shadow-xl transition"
                    >
                        <img src="/images/bot-avator.png" alt="Bot" className="w-8 h-8 rounded-full" />
                        <span className="font-medium text-sm text-gray-700">Ask TrustBot</span>
                    </div>

                    <div
                        onClick={(e) => {
                            e.stopPropagation();
                            handleTemporaryHide();
                        }}
                        className="text-gray-500 hover:text-red-500 cursor-pointer text-xl"
                    >
                        &times;
                    </div>
                </div>
            )}

            {isOpen && (
                <div className={`relative bg-white shadow-xl rounded-xl flex flex-col mt-4 transition-all duration-300 ${isExpanded ? 'w-[400px] h-[600px]' : 'w-80 h-96'}`}>
                    <ChatWindow
                        messages={messages}
                        onQuickReply={handleQuickReply}
                        chatEndRef={chatEndRef}
                        onFeedbackSubmit={handleFeedbackSubmit}
                        isExpanded={isExpanded}
                        toggleExpand={toggleExpand}
                        onExitClick={handleExitClick}
                        onRefreshClick={handleRefreshChat}
                        isRefreshing={isRefreshing}
                        isTyping={isTyping || isFeedbackSending}
                    />

                    <div className="p-2 bg-white flex flex-col border-t relative">
                        <div className="flex items-center">
                            <input
                                type="text"
                                ref={inputRef}
                                value={input}
                                onChange={handleInputChange}
                                placeholder="Type a message..."
                                className="flex-1 border rounded-lg px-3 py-2 text-sm focus:outline-none"
                                onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            />
                            <button
                                onClick={handleSend}
                                disabled={!input.trim()}
                                className={`ml-2 ${input.trim() ? 'text-blue-600 hover:text-blue-800' : 'text-gray-300 cursor-not-allowed'}`}
                            >
                                <SendHorizontal size={20} />
                            </button>
                        </div>

                        {suggestions.length > 0 && (
                            <div className="absolute bottom-14 left-2 right-2 bg-white shadow-lg rounded-md border max-h-40 overflow-y-auto z-10">
                                {suggestions.map((suggestion, index) => (
                                    <div
                                        key={index}
                                        onClick={() => handleSuggestionClick(suggestion)}
                                        className="px-3 py-2 hover:bg-gray-100 cursor-pointer text-sm"
                                    >
                                        {suggestion}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
});

export default ChatbotContainer;
