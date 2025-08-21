import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Login = () => {
    const [agentId, setAgentId] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    const handleLogin = async () => {
        if (agentId.trim() && password.trim()) {
            try {
                const response = await fetch('http://localhost:5001/agent_login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ agent_id: agentId, password }),
                });

                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);

                const data = await response.json();

                if (data.status === 'success') {
                    localStorage.setItem('agentId', agentId);
                    localStorage.setItem('isAdmin', data.is_admin);

                    if (Number(data.is_admin) === 1) {
                        navigate('/admin');
                    } else {
                        navigate('/dashboard');
                    }
                } else {
                    alert(data.message || 'Invalid credentials');
                }
            } catch (error) {
                console.error('Login Error:', error);
                alert('Unable to connect to the server. Please try again later.');
            }
        } else {
            alert('Enter Agent ID and Password');
        }
    };

    return (
        <div className="flex justify-center items-center h-screen">
            <div className="p-8 border rounded shadow-md w-96">
                <h2 className="text-2xl font-semibold mb-6">Agent Login</h2>
                <input
                    type="text"
                    placeholder="Agent ID"
                    value={agentId}
                    onChange={e => setAgentId(e.target.value)}
                    className="w-full border px-3 py-2 mb-4 rounded"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={e => setPassword(e.target.value)}
                    className="w-full border px-3 py-2 mb-4 rounded"
                />
                <button onClick={handleLogin} className="w-full bg-blue-600 text-white py-2 rounded">
                    Login
                </button>
            </div>
        </div>
    );
};

export default Login;
