import React, { useState, useEffect, useRef } from 'react';
import { Maximize2, Minimize2, RefreshCw, X, ThumbsUp, ThumbsDown, ArrowLeft, ArrowRight } from 'lucide-react';

const ChatWindow = ({
    messages,
    onQuickReply,
    onFeedbackSubmit,
    chatEndRef,
    isExpanded,
    toggleExpand,
    onExitClick,
    onRefreshClick,
    isRefreshing,
    isTyping
}) => {
    const [feedbackState, setFeedbackState] = useState({});
    const carouselRef = useRef(null); // carousel container ref

    useEffect(() => {
        if (chatEndRef.current) {
            chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [messages, isTyping]);

    const handleFeedbackClick = (msgId, type) => {
        setFeedbackState({
            ...feedbackState,
            [msgId]: { feedbackType: type, showInput: true, feedbackText: '' }
        });
    };

    const handleFeedbackTextChange = (msgId, text) => {
        setFeedbackState({
            ...feedbackState,
            [msgId]: { ...feedbackState[msgId], feedbackText: text }
        });
    };

    const formatTimestamp = (timestamp) => {
        const date = new Date(timestamp);
        const now = new Date();

        const isToday = date.toDateString() === now.toDateString();
        const yesterday = new Date();
        yesterday.setDate(now.getDate() - 1);
        const isYesterday = date.toDateString() === yesterday.toDateString();

        if (isToday) {
            return `Today • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        } else if (isYesterday) {
            return `Yesterday • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        } else {
            return `${date.toLocaleDateString()} • ${date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="bg-blue-600 text-white p-3 rounded-t-xl flex justify-between items-center">
                <div>
                    <div className="text-lg font-bold">TrustBot by Cloudforce</div>
                    <div className="text-xs text-gray-200">trustbot ai</div>
                </div>
                <div className="flex items-center space-x-3">
                    <button onClick={toggleExpand} className="hover:text-gray-200">
                        {isExpanded ? <Minimize2 size={18} /> : <Maximize2 size={18} />}
                    </button>
                    <button onClick={onRefreshClick} className="hover:text-gray-200">
                        {isRefreshing ? (
                            <RefreshCw size={18} className="animate-spin" />
                        ) : (
                            <RefreshCw size={18} />
                        )}
                    </button>
                    <button onClick={onExitClick} className="hover:text-gray-200">
                        <X size={18} />
                    </button>
                </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-3 space-y-3 bg-gray-100">
                {messages.map((msg, index) => (
                    <div key={index} className={`flex items-end ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
                        {/* Avatar */}
                        {(msg.sender === 'bot' || msg.sender === 'agent') && (
                            <img
                                src={msg.sender === 'bot' ? '/images/toggle.png' : '/images/live_agent.png'}
                                alt={`${msg.sender} Avatar`}
                                className="w-8 h-8 rounded-full mr-2"
                            />
                        )}

                        {/* Message Bubble */}
                        <div className="flex flex-col max-w-xs relative">
                            <div className={`p-2 max-w-xs rounded-2xl ${msg.sender === 'user'
                                ? 'bg-gradient-to-r from-blue-500 to-blue-700 text-white shadow-md'
                                : msg.sender === 'agent'
                                    ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white shadow-md'
                                    : 'bg-white shadow'
                                }`}>
                                <div>{msg.text}</div>

                                {/* Quick Replies */}
                                {msg.buttons && msg.buttons.length > 0 && (
                                    <div className="flex flex-wrap gap-2 mt-2">
                                        {msg.buttons.map((btn, idx) => (
                                            <button
                                                key={idx}
                                                onClick={() => !btn.disabled && onQuickReply(btn.title, btn.payload, index, btn.type)}
                                                disabled={btn.disabled}
                                                className={`px-4 py-1.5 text-sm rounded-full ${btn.disabled ? 'bg-gray-300 cursor-not-allowed' : 'bg-gradient-to-r from-green-400 to-green-600 text-white'} font-semibold shadow-md hover:shadow-lg hover:brightness-105 transition-all duration-200`}
                                            >
                                                {btn.title}
                                            </button>
                                        ))}
                                    </div>
                                )}

                                {/* Carousel with Arrows */}
                                {msg.carousel && msg.carousel.length > 0 && (
                                    <div className="mt-2 relative">
                                        {/* Left Arrow */}
                                        <button
                                            onClick={() => carouselRef.current.scrollBy({ left: -250, behavior: 'smooth' })}
                                            className="absolute -left-3 top-1/2 transform -translate-y-1/2 bg-white rounded-full shadow p-1 hover:bg-gray-200 z-10"
                                        >
                                            <ArrowLeft size={18} />
                                        </button>

                                        {/* Scrollable Carousel */}
                                        <div
                                            ref={carouselRef}
                                            className="flex gap-3 pb-2 scroll-smooth overflow-hidden"
                                            style={{ scrollBehavior: 'smooth' }}
                                        >
                                            {msg.carousel.map((card, cidx) => (
                                                <div
                                                    key={cidx}
                                                    className={`bg-white border rounded-lg shadow p-3 ${isExpanded ? 'min-w-[220px]' : 'min-w-[160px]'
                                                        }`}
                                                >
                                                    {card.image_url && (
                                                        <img src={card.image_url} alt={card.title} className="w-full h-28 object-cover rounded-md mb-2" />
                                                    )}
                                                    <div className="font-semibold text-sm">{card.title}</div>
                                                    {card.subtitle && <div className="text-xs text-gray-500">{card.subtitle}</div>}
                                                    {card.buttons && (
                                                        <div className="flex flex-wrap gap-2 mt-2">
                                                            {card.buttons.map((b, bi) => (
                                                                <button
                                                                    key={bi}
                                                                    onClick={() => !b.disabled && onQuickReply(b.title, b.payload, index, b.type)}
                                                                    disabled={b.disabled}
                                                                    className={`px-3 py-1 text-xs rounded-full ${b.disabled ? 'bg-gray-300 cursor-not-allowed' : 'bg-gradient-to-r from-green-400 to-green-600 text-white'} font-semibold`}
                                                                >
                                                                    {b.title}
                                                                </button>
                                                            ))}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>

                                        {/* Right Arrow */}
                                        <button
                                            onClick={() => carouselRef.current.scrollBy({ left: 250, behavior: 'smooth' })}
                                            className="absolute -right-3 top-1/2 transform -translate-y-1/2 bg-white rounded-full shadow p-1 hover:bg-gray-200 z-10"
                                        >
                                            <ArrowRight size={18} />
                                        </button>
                                    </div>
                                )}
                            </div>

                            {/* Timestamp */}
                            <div className={`text-[10px] text-gray-400 mt-1 ${msg.sender === 'user' ? 'text-right' : 'text-left'}`}>
                                {formatTimestamp(msg.timestamp)}
                            </div>

                            {/* Feedback */}
                            {msg.sender === 'bot' && !feedbackState[msg.id]?.showInput && (
                                <div className="flex justify-end space-x-2 mt-1">
                                    <ThumbsUp size={16} className="cursor-pointer text-gray-500 hover:text-blue-600" onClick={() => handleFeedbackClick(msg.id, 'like')} />
                                    <ThumbsDown size={16} className="cursor-pointer text-gray-500 hover:text-red-500" onClick={() => handleFeedbackClick(msg.id, 'dislike')} />
                                </div>
                            )}

                            {/* Feedback Text Input */}
                            {feedbackState[msg.id]?.showInput && (
                                <div className="flex space-x-2 mt-1">
                                    <input
                                        type="text"
                                        className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm"
                                        placeholder="Enter your feedback..."
                                        value={feedbackState[msg.id].feedbackText}
                                        onChange={(e) => handleFeedbackTextChange(msg.id, e.target.value)}
                                    />
                                    <button
                                        className="bg-blue-600 text-white text-sm px-3 py-1 rounded hover:bg-blue-700"
                                        onClick={() => {
                                            onFeedbackSubmit(msg.id, feedbackState[msg.id].feedbackType, feedbackState[msg.id].feedbackText);
                                            setFeedbackState({ ...feedbackState, [msg.id]: null });
                                        }}
                                    >
                                        Send
                                    </button>
                                </div>
                            )}
                        </div>

                        {/* User Avatar */}
                        {msg.sender === 'user' && (
                            <img src="/images/bot-avatar.png" alt="User Avatar" className="w-8 h-8 rounded-full ml-2" />
                        )}
                    </div>
                ))}

                {/* Typing Animation */}
                {isTyping && (
                    <div className="flex items-start space-x-2">
                        <img src="/images/toggle.png" alt="Bot Avatar" className="w-8 h-8 rounded-full" />
                        <div className="bg-white shadow rounded-lg px-3 py-2 flex items-center space-x-1">
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-150"></span>
                            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-300"></span>
                        </div>
                    </div>
                )}

                <div ref={chatEndRef}></div>
            </div>
        </div>
    );
};

export default ChatWindow;
