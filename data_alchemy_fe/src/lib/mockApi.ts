import {Column, DataRow, FileUploadResponse, TaskStatus} from "../models/DataInference/dataInference.models.ts.tsx";
import {ApiResponse} from "../types/common.types.ts";

// Mock delay function
const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

// Mock data
const mockColumns: Column[] = [
    {id: '1', name: 'id', columnIndex: 0, inferredType: 'int64', customUserType: '' },
    {id: '2', name: 'name', columnIndex: 1, inferredType: 'object', customUserType: '' },
    {id: '3', name: 'age', columnIndex: 2, inferredType: 'int64', customUserType: '' },
    {id: '4', name: 'email', columnIndex: 3, inferredType: 'object', customUserType: '' },
    {id: '5', name: 'date_joined', columnIndex: 4, inferredType: 'datetime64', customUserType: '' }
];

const mockDataRows: DataRow[] = Array.from({ length: 100 }, (_, i) => ({
    id: i + 1,
    name: `User ${i + 1}`,
    age: Math.floor(Math.random() * 50) + 20,
    email: `user${i + 1}@example.com`,
    dateJoined: new Date(Date.now() - Math.random() * 10000000000).toISOString()
}));

// Mock API functions
export const mockUploadFile = async (file: File): Promise<ApiResponse<FileUploadResponse>> => {
    await delay(1000); // Simulate network delay

    return {
        status: 'success',
        message: 'File uploaded successfully',
        code: 200,
        data: {
            taskId: 'mock-task-123',
            datasetId: 'mock-file-123'
        }
    };
};

export const mockGetTaskStatus = async (taskId: string, progress: number): Promise<ApiResponse<TaskStatus>> => {
    await delay(500);

    return {
        status: 'success',
        message: 'Task status retrieved',
        code: 200,
        data: {
            status: progress === 100 ? 'SUCCESS' : 'PROGRESS',
            progress
        }
    };
};

export const mockGetColumns = async (fileId: string): Promise<ApiResponse<Column[]>> => {
    await delay(500);
    return {
        status: 'success',
        message: 'Columns retrieved successfully',
        code: 200,
        data: mockColumns
    };

};

export const mockGetProcessedData = async (page: number): Promise<ApiResponse<DataRow[]>> => {
    await delay(500);
    const start = (page - 1) * 50;
    const end = start + 50;

    return {
        status: 'success',
        message: 'Data retrieved successfully',
        code: 200,
        data: mockDataRows.slice(start, end),
        pagination: {
            count: mockDataRows.length,
            currentPage: page,
            totalPages: Math.ceil(mockDataRows.length / 50),
            pageSize: 50,
            next: page * 50 < mockDataRows.length ? `?page=${page + 1}` : null,
            previous: page > 1 ? `?page=${page - 1}` : null
        }
    };
};

export const mockUpdateColumnType = async (columnName: string, newType: string): Promise<ApiResponse<FileUploadResponse>> => {
    await delay(500);

    return {
        status: 'success',
        message: 'Column type updated successfully',
        code: 200,
        data: {
            taskId: 'mock-task-1234',
            datasetId: 'mock-file-1234'
        }
    };
};