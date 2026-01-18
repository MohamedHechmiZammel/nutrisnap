import { LogBox } from 'react-native';

// Ignore specific logs (optional)
LogBox.ignoreLogs(['Require cycle:']);

// Global styling constants
export const COLORS = {
    primary: '#2E7D32', // Green
    secondary: '#FF6F00', // Amber/Orange
    background: '#F5F5F5',
    card: '#FFFFFF',
    text: '#212121',
    textSecondary: '#757575',
    error: '#D32F2F',
    success: '#388E3C',
};

// Valid test user ID from seed_db.py
export const TEST_USER_ID = "696d20934f2b5ddfb81d2da1"; 
