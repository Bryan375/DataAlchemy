import axios from 'axios';
import {ApiResponse} from "../types/common.types.ts";
import {FileUploadResponse, TaskStatus} from "../models/DataInference/dataInference.models.ts.tsx";

const API_BASE_URL = 'http://localhost:8000/api/v1';

const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000
});

export const uploadFile = async (file: File): Promise<ApiResponse<FileUploadResponse>> => {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ApiResponse<FileUploadResponse>>('/datasets/', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getTaskStatus = async (datasetId: string, taskId: string): Promise<ApiResponse<TaskStatus>> => {
    const response = await apiClient.get<ApiResponse<TaskStatus>>(`/datasets/${datasetId}/status`, {
        params: { taskId: taskId }
    });
    return response.data;
};

export const getDatasetDetails = async (datasetId: string, page: number = 1) => {
    const response = await apiClient.get(`/datasets/${datasetId}/`, {
        params: { page },
    });
    return response.data;
};

export const updateColumnType = async (columnId: string, datasetId: string, targetType: string) => {
    const response = await apiClient.put(`/columns/${columnId}/type_conversion/`, {
        datasetId,
        targetType,
    });
    return response.data;
};