import { ChangeEvent } from "react"
import {Column, Data, DataRow} from "../../models/DataInference/dataInference.models.ts.tsx";
import {PaginationMeta} from "../common.types.ts";

export interface DataInferenceFileUploaderProps {
    file: File | undefined
    isLoading: boolean
    onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void
    OnSubmit: () => void
}

export interface DataInferenceTemplateProps {
    file: File | undefined
    isLoading: boolean
    progress: number
    data: Data | null
    onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void
    onSubmit: () => void
    onTypeChange: (column: Column, newType: string | null) => void
    onApplyChanges: () => void
    currentPage: number
    setCurrentPage: (page: number) => void
}

export interface ProcessingProgressProps {
    progress: number
}

export interface DataTypesTableProps {
    columnDetails: Column[]
    onTypeChange: (column: Column, newType: string | null) => void
    onApplyChanges: () => void
}

export interface TypeChangeDialogProps {
    column: Column
    currentType: string
    onTypeChange: (column: Column, newType: string | null) => void
    onApplyChanges: () => void
}

export interface DataTypeSelectorProps {
    onTypeChange: (value: string) => void
}

export interface DataTableProps {
    data: DataRow[];
    columns: Column[];
    pagination: PaginationMeta;
    currentPage: number;
    onPageChange: (page: number) => void;
}

export interface PaginationProps {
    currentPage: number;
    totalPages: number;
    onPageChange: (page: number) => void;
}
