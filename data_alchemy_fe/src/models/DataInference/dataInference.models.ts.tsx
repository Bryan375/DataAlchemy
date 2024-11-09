import {PaginationMeta} from "@/types/common.types.ts";

export interface Data {
    column: Column[]
    dataRows: DataRow[]
    pagination: PaginationMeta
}

export interface Column {
    name: string
    columnIndex: number
    inferredType: string
    customUserType: string
}

export interface DataRow {
    [key: string]: string | number | boolean | null
}

export interface CustomInferredTypes {
    column: Column
    newType: string
}

export interface TaskStatus {
    status: 'in_progress' | 'completed' | 'failed';
    progress: number;
    message?: string;
    fileId: string;
}

export interface FileUploadResponse {
    taskId: string;
    fileId: string;
}