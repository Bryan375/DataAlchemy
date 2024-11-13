import {PaginationMeta} from "../../types/common.types.ts";

export interface Data {
    column: Column[]
    dataRows: DataRow[]
    pagination: PaginationMeta
}

export interface Column {
    id: string
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
    status: 'PROGRESS' | 'SUCCESS' | 'FAILED';
    progress: number;
}

export interface FileUploadResponse {
    taskId: string;
    datasetId: string;
}