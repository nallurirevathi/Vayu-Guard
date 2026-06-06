const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
require('dotenv').config();

const app = express();

// Middleware
app.use(cors()); 
app.use(express.json()); 

// Import Routes
const authRoutes = require('./routes/authRoutes');

// Database Connection
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('✅ MongoDB Connected Successfully'))
  .catch((err) => console.log('❌ MongoDB Connection Error: ', err));

// Route Middleware
app.use('/api/auth', authRoutes);

// Basic Health Check Route
app.get('/api/status', (req, res) => {
    res.json({ status: 'MERN Backend is running', version: '1.0' });
});

// Start the Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 VayuGuard Backend running on http://localhost:${PORT}`);
});