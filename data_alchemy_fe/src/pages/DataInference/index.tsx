import {ChangeEvent, FC, useEffect, useState} from 'react';
import {DataInferenceTemplate} from "@/components/templates/DataInference/DataInferenceTemplate.tsx";
import {
    Column,
    CustomInferredTypes,
    Data,
    TaskStatus
} from "@/models/DataInference/dataInference.models.ts.tsx";
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import {getColumns, getProcessedData, getTaskStatus, updateColumnType, uploadFile} from "@/lib/api.ts";
import toast from "react-hot-toast";
import {ApiError, ValidationError} from "@/lib/error.ts";

export const DataInference: FC = () => {
    const [file, setFile] = useState<File>();
    const [fileId, setFileId] = useState<string>('');
    const [data, setData] = useState<Data | null>(null);
    const [customInferredTypes, setCustomInferredTypes] = useState<CustomInferredTypes | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [progress, setProgress] = useState<number>(0);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [taskId, setTaskId] = useState<string | null>(null);
    const itemsPerPage = 20;

    const queryClient = useQueryClient();

    const uploadMutation = useMutation({
        mutationFn: (file: File) => uploadFile(file),
        onSuccess: (response) => {
            if (response.status === 'success') {
                setTaskId(response.data.taskId);
                setFileId(response.data.fileId);
            } else {
                toast.error(`Upload failed: ${response.message}`);
            }
        }
    })

    const updateTypeMutation = useMutation({
        mutationFn: ({ columnName, newType }: { columnName: string, newType: string }) => updateColumnType(columnName, newType),
        onSuccess: (response) => {
            queryClient.invalidateQueries({ queryKey: ['inferredData'] });
            if (response.status === 'success') {
                setTaskId(response.data.taskId);
                setFileId(response.data.fileId);
                toast.success('Column type updated successfully');
            } else {
                toast.error(`Upload failed: ${response.message}`);
            }
        },
        onError: () => {
            toast.error('Failed to update column type');
        }
    });

    const columnsDataQuery = useQuery({
        queryKey: ['inferredData', fileId],
        queryFn: async () => {
            try {
                return await getColumns(fileId)
            } catch (error) {
                if (error instanceof ValidationError || error instanceof ApiError) {
                    throw error;
                }
                console.error('Unexpected error while fetching columns:', error);
                throw new ApiError('An unexpected error occurred while fetching columns', 500);
            }
        },
        enabled: false
    })

    const dataQuery = useQuery({
        queryKey: ['dataRows', fileId, currentPage],
        queryFn: async () => {
            try {
                return await getProcessedData(currentPage)
            } catch (error) {
                if (error instanceof ValidationError || error instanceof ApiError) {
                    throw error;
                }
                console.error('Unexpected error while fetching columns:', error);
                throw new ApiError('An unexpected error occurred while fetching columns', 500);
            }
        },
        enabled: false
    })


    useEffect(() => {
        let intervalId: number;
        let progressTemp = 0;
        setData(null);

        if (taskId) {
            setIsLoading(true);
            intervalId = window.setInterval(async () => {
                try {
                    progressTemp += 50;
                    const response = await getTaskStatus(taskId, progressTemp);
                    const status: TaskStatus = response.data;
                    setProgress(status.progress);

                    if (status.status === 'completed') {
                        clearInterval(intervalId);
                        const [columnsResponse, dataResponse] = await Promise.all([
                            columnsDataQuery.refetch(),
                            dataQuery.refetch()
                        ]);
                        
                        if (columnsResponse.data?.status === 'success' && 
                            dataResponse.data?.status === 'success') {
                            setData({
                                column: columnsResponse.data.data,
                                dataRows: dataResponse.data.data,
                                pagination: dataResponse.data.pagination
                            })
                            toast.success('File processing completed');
                        } else {
                            toast.error('Error loading data');
                        }
                        setIsLoading(false);
                    } else if (status.status === 'failed') {
                        clearInterval(intervalId);
                        toast.error('File processing failed');
                        setIsLoading(false);
                    }
                } catch (error) {
                    clearInterval(intervalId);
                    toast.error('Error checking processing status');
                }
            }, 1000);
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [taskId]);

    const handleSubmit = async (): Promise<void> => {
        if (file) {
            setProgress(0);
            await uploadMutation.mutateAsync(file);
        }
    }

    const fileUpload = (event: ChangeEvent<HTMLInputElement>): void => {
        const files = event.target.files;
        if (files) {
            setFile(files[0]);
        }
    }

    const onTypeChange = (column: Column, newType: string | null): void => {
        if (column && !newType) {
            setCustomInferredTypes(null);
        }
        else if (newType && column.customUserType !== newType) {
            setCustomInferredTypes({ column, newType });
        }
    }

    const onApplyChange = async (): Promise<void> => {
        if (customInferredTypes) {
            setProgress(0)
            await updateTypeMutation.mutateAsync({ columnName: customInferredTypes.column.name, newType: customInferredTypes.newType });
            setCustomInferredTypes(null);

        }
    }

    return (
        <DataInferenceTemplate
            file={file}
            isLoading={isLoading}
            progress={isLoading ? progress : 100}
            data={data}
            onFileSelect={fileUpload}
            onSubmit={handleSubmit}
            onTypeChange={onTypeChange}
            onApplyChanges={onApplyChange}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
            itemsPerPage={itemsPerPage}
        />
    );
};