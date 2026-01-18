import axios from 'axios';
import { Platform } from 'react-native';
import { AnalyzeImageResponse, LogMealRequest, MealLog, DashboardResponse } from '../types';

// Dynamic API URL based on platform
const API_URL = Platform.OS === 'web'
    ? 'http://localhost:8000'
    : 'http://10.0.2.2:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const checkHealth = async (): Promise<boolean> => {
    try {
        const response = await api.get('/health');
        return response.data.status === 'healthy';
    } catch (error) {
        console.error('Health check failed:', error);
        return false;
    }
};

export const analyzeImage = async (imageUri: string): Promise<AnalyzeImageResponse> => {
    const formData = new FormData();

    if (Platform.OS === 'web') {
        // Web: Fetch the URI to get a Blob, then append
        const response = await fetch(imageUri);
        const blob = await response.blob();
        // Ensure we send a valid image type
        formData.append('image', blob, 'food.jpg');
    } else {
        // Mobile: Append object with uri, name, type
        const filename = imageUri.split('/').pop();
        const match = /\.(\w+)$/.exec(filename || '');
        const type = match ? `image/${match[1]}` : `image/jpeg`;

        formData.append('image', {
            uri: imageUri,
            name: filename || 'food.jpg',
            type,
        } as any);
    }

    try {
        // Use raw axios to avoid default instance headers (JSON) interfering with Multipart
        const response = await axios.post<AnalyzeImageResponse>(`${API_URL}/analyze`, formData, {
            headers: {
                ...(Platform.OS !== 'web' ? { 'Content-Type': 'multipart/form-data' } : {}),
                // On Web, do NOT set Content-Type; browser handles it
            },
            transformRequest: (data) => data, // Prevent axios from transforming FormData
        });
        return response.data;
    } catch (error: any) {
        if (axios.isAxiosError(error) && error.response) {
            console.error('Analyze Error Response:', error.response.status, error.response.data);
        } else {
            console.error('Analyze Error:', error);
        }
        throw error;
    }
};

export const logMeal = async (data: LogMealRequest): Promise<MealLog> => {
    try {
        const response = await api.post<MealLog>('/log-meal', data);
        return response.data;
    } catch (error) {
        console.error('Log meal error:', error);
        throw error;
    }
};

export const getDashboard = async (userId: string): Promise<DashboardResponse> => {
    try {
        const response = await api.get<DashboardResponse>(`/dashboard/${userId}`);
        return response.data;
    } catch (error) {
        console.error('Dashboard error:', error);
        throw error;
    }
};

export default api;
