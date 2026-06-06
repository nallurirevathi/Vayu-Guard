const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    name: { type: String, required: true },
    email: { type: String, required: true, unique: true },
    password: { type: String, required: true },
    // This is the crucial field your AI will use later for health advisories!
    healthProfile: { 
        type: String, 
        default: 'none', 
        enum: ['none', 'asthma', 'elderly', 'outdoor_worker'] 
    }
}, { timestamps: true });

module.exports = mongoose.model('User', userSchema);