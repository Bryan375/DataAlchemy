export interface Data {
    column: Column[]
    dataRows: DataRow[]
}

export interface Column {
    name: string
    inferredType: string
    userType: string
}

export interface DataRow {
    [key: string]: string | number | boolean | null
}

export interface CustomInferredTypes {
    column: Column
    newType: string
}