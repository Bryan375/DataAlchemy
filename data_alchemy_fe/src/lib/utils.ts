import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import {ValidationError} from "./error.ts";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export const validateFile = (file: File | null): void => {
  if (!file) {
      throw new ValidationError('No file provided');
  }

  // File size validation (e.g., 100MB limit)
  const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB in bytes
  if (file.size > MAX_FILE_SIZE) {
      throw new ValidationError('File size exceeds 100MB limit');
  }

  // File type validation
  const ALLOWED_TYPES = [
      'text/csv',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
  ];
  if (!ALLOWED_TYPES.includes(file.type)) {
      throw new ValidationError('Invalid file type. Please upload a CSV or Excel file');
  }
}