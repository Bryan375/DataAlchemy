interface ApiResponseMeta {
    status: string;
    message: string;
    code: number;
}

export interface SuccessResponse<T> extends ApiResponseMeta {
    status: 'success'
    data: T
    pagination?: PaginationMeta
    errors?: never
}

export interface ErrorResponse extends ApiResponseMeta {
    status: 'error'
    errors: { [key: string]: string[] }
    data?: never
    pagination?: never
}

export interface PaginationMeta {
    count: number;
    next?: string | null;
    previous?: string | null;
    currentPage: number;
    totalPages: number;
    pageSize: number;
}

export type ApiResponse<T> = SuccessResponse<T> | ErrorResponse;