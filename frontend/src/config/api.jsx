// API configuration
export const API_URL = process.env.REACT_APP_API_URL;

if (!API_URL) {
    console.warn('REACT_APP_API_URL is not defined in environment variables');
} 