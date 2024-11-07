import { ChangeEvent } from "react"

// Types
export type DataType = 'int64' | 'float64' | 'object' | 'datetime64' | 'bool' | 'category';
export type DataPreviewTableProps = DataState
export type PreviewData = { [key: string]: string | number | boolean | null }


// Interfaces
export interface DataInferenceFileUploaderProps {
    file: File | null
    isLoading: boolean
    onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void
    OnSubmit: () => void
}

export interface DataState {
    columnDetails: Column[]
    previewData: PreviewData[]
}

export interface Column {
    name: string
    inferredType: string
    userType: string
}

export interface PreviewChange {
    columnName: string
    newType: string
}

export interface DataInferenceTemplateProps {
  file: File | null
  isLoading: boolean
  progress: number
  data: DataState | null
  previewChanges: PreviewChange | null
  onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void
  onSubmit: () => void
  onTypeChange: (columnName: string, newType: string) => void
  onApplyChanges: () => void
  onDownload: () => void
}

export interface ProcessingProgressProps {
    progress: number
}

export interface DataTypesTableProps {
    columnDetails: Column[]
    onTypeChange: (columnName: string, newType: string) => void
    onApplyChanges: () => void
    previewChanges: PreviewChange | null
}

export interface TypeChangeDialogProps {
    column: Column
    currentType: string
    onTypeChange: (columnName: string, newType: string) => void
    previewChanges: PreviewChange | null
    onApplyChanges: () => void
}

export interface DataTypeSelectorProps {
    onTypeChange: (value: string) => void
}
