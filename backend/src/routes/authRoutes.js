const express = require('express');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');

const router = express.Router();

// POST /api/auth/register
router.post('/register', async (req, res) => {
    try {
        const { name, email, password, healthProfile } = req.body;

        // 1. Check if user already exists
        const existingUser = await User.findOne({ email });
        if (existingUser) {
            return res.status(400).json({ error: 'Email already in use' });
        }

        // 2. Hash the password
        const salt = await bcrypt.genSalt(10);
        const hashedPassword = await bcrypt.hash(password, salt);

        // 3. Save the new user
        const newUser = new User({
            name,
            email,
            password: hashedPassword,
            healthProfile: healthProfile || 'none'
        });

        await newUser.save();
        res.status(201).json({ message: 'User registered successfully!', user: newUser.name });

    } catch (error) {
        res.status(500).json({ error: 'Server error during registration' });
    }
});

// POST /api/auth/login
router.post('/login', async (req, res) => {
    try {
        const { email, password } = req.body;

        // 1. Check if the user exists
        const user = await User.findOne({ email });
        if (!user) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }

        // 2. Verify the password
        const isMatch = await bcrypt.compare(password, user.password);
        if (!isMatch) {
            return res.status(400).json({ error: 'Invalid credentials' });
        }

        // 3. Generate the VIP Pass (JWT)
        const token = jwt.sign(
            { userId: user._id, healthProfile: user.healthProfile },
            process.env.JWT_SECRET,
            { expiresIn: '24h' }
        );

        res.json({ message: 'Login successful!', token, healthProfile: user.healthProfile });

    } catch (error) {
        res.status(500).json({ error: 'Server error during login' });
    }
});

module.exports = router;