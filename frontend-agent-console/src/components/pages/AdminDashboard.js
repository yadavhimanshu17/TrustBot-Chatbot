import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
    const [agents, setAgents] = useState([]);
    const [formData, setFormData] = useState({ agent_id: '', agent_name: '', email: '', password: '' });
    const [isEditing, setIsEditing] = useState(false);

    const navigate = useNavigate();

    const fetchAgents = async () => {
        const response = await fetch('http://localhost:5001/admin/get_agents');
        const data = await response.json();
        setAgents(data);
    };

    useEffect(() => {
        fetchAgents();
    }, []);

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleAddAgent = async () => {
        const response = await fetch('http://localhost:5001/admin/add_agent', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
        });
        if (response.ok) {
            alert('Agent Added');
            fetchAgents();
            setFormData({ agent_id: '', agent_name: '', email: '', password: '' });
        } else {
            const err = await response.json();
            alert(err.message);
        }
    };

    const handleDeleteAgent = async (agentId) => {
        if (window.confirm(`Delete Agent ${agentId}?`)) {
            await fetch(`http://localhost:5001/admin/delete_agent/${agentId}`, { method: 'DELETE' });
            fetchAgents();
        }
    };

    const handleEditAgent = (agent) => {
        setFormData({
            agent_id: agent.agent_id,
            agent_name: agent.agent_name,
            email: agent.email,
            password: '', // password not needed for update
        });
        setIsEditing(true);
    };

    const handleUpdateAgent = async () => {
        const response = await fetch(`http://localhost:5001/admin/update_agent/${formData.agent_id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                agent_name: formData.agent_name,
                email: formData.email,
            }),
        });

        if (response.ok) {
            alert('Agent Updated');
            fetchAgents();
            setFormData({ agent_id: '', agent_name: '', email: '', password: '' });
            setIsEditing(false);
        } else {
            const err = await response.json();
            alert(err.message);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('agentId');
        localStorage.removeItem('isAdmin');
        navigate('/');
    };

    return (
        <div className="p-6">
            {/* Header + Logout */}
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-3xl font-bold">Admin Dashboard - Manage Agents</h1>
                <button
                    onClick={handleLogout}
                    className="bg-red-500 text-white px-4 py-2 rounded"
                >
                    Logout
                </button>
            </div>

            {/* Add / Update Agent Form */}
            <div className="mb-6">
                <h2 className="text-xl font-semibold mb-2">{isEditing ? 'Update Agent' : 'Add New Agent'}</h2>
                <input name="agent_id" placeholder="Agent ID" value={formData.agent_id} onChange={handleInputChange} className="border p-2 mr-2" disabled={isEditing} />
                <input name="agent_name" placeholder="Name" value={formData.agent_name} onChange={handleInputChange} className="border p-2 mr-2" />
                <input name="email" placeholder="Email" value={formData.email} onChange={handleInputChange} className="border p-2 mr-2" />
                {!isEditing && (
                    <input name="password" placeholder="Password" type="password" value={formData.password} onChange={handleInputChange} className="border p-2 mr-2" />
                )}
                {isEditing ? (
                    <button onClick={handleUpdateAgent} className="bg-yellow-500 text-white px-4 py-2 rounded">Update Agent</button>
                ) : (
                    <button onClick={handleAddAgent} className="bg-green-500 text-white px-4 py-2 rounded">Add Agent</button>
                )}
            </div>

            {/* Agent List */}
            <div>
                <h2 className="text-xl font-semibold mb-4">Existing Agents</h2>
                <table className="w-full border-collapse">
                    <thead>
                        <tr>
                            <th className="border p-2">Agent ID</th>
                            <th className="border p-2">Name</th>
                            <th className="border p-2">Email</th>
                            <th className="border p-2">Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        {agents.map(agent => (
                            <tr key={agent.agent_id}>
                                <td className="border p-2">{agent.agent_id}</td>
                                <td className="border p-2">{agent.agent_name}</td>
                                <td className="border p-2">{agent.email}</td>
                                <td className="border p-2 flex gap-2">
                                    <button onClick={() => handleEditAgent(agent)} className="bg-blue-500 text-white px-3 py-1 rounded">Edit</button>
                                    <button onClick={() => handleDeleteAgent(agent.agent_id)} className="bg-red-500 text-white px-3 py-1 rounded">Delete</button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AdminDashboard;
