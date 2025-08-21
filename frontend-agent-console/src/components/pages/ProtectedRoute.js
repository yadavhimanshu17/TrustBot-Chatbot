// src/components/pages/ProtectedRoute.js

import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
    const agentId = localStorage.getItem('agentId');

    if (!agentId) {
        return <Navigate to="/" replace />;
    }

    return children;
};
export default ProtectedRoute;
