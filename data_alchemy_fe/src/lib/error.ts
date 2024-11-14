export class ValidationError extends Error {
    constructor(message: string) {
        super(message);
        this.name = 'ValidationError';
    }
}

export class ApiError extends Error {
    constructor(message: string, public code: number) {
        super(message);
        this.name = 'ApiError';
    }
}