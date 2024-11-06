import { ChangeEvent } from "react"

export interface DataInferenceFileUploaderProps {
    file: File | null
    isLoading: boolean
    onFileSelect: (event: ChangeEvent<HTMLInputElement>) => void
    OnSubmit: () => void
}

export interface DataState {
    columnDetails: Column[]
    previewData: { [key: string]: string | number | boolean | Date | null }[];
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
    progress: number;
}
