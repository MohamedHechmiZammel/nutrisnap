import { Platform } from 'react-native';

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

    // React Native handling for file uploads
    const filename = imageUri.split('/').pop();
    const match = /\.(\w+)$/.exec(filename || '');
    const type = match ? `image/${match[1]}` : `image`;

    formData.append('image', {
        uri: imageUri,
        name: filename,
        type,
    } as any);

    try {
        const response = await api.post<AnalyzeImageResponse>('/analyze', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });
        return response.data;
    } catch (error) {
        console.error('Analyze image error:', error);
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
