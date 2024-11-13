import {ChangeEvent, FC, useEffect, useState} from 'react';
import {useMutation, useQuery, useQueryClient} from "@tanstack/react-query";
import toast from "react-hot-toast";
import {getDatasetDetails, getTaskStatus, updateColumnType, uploadFile} from "../../lib/api.ts";
import {Column, CustomInferredTypes, Data, TaskStatus} from "../../models/DataInference/dataInference.models.ts.tsx";
import {ApiError, ValidationError} from "../../lib/error.ts";
import {DataInferenceTemplate} from "../../components/templates/DataInference/DataInferenceTemplate.tsx";

export const DataInference: FC = () => {
    const [file, setFile] = useState<File>();
    const [datasetId, setdatasetId] = useState<string>('');
    const [data, setData] = useState<Data | null>(null);
    const [customInferredTypes, setCustomInferredTypes] = useState<CustomInferredTypes | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [progress, setProgress] = useState<number>(0);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const [taskId, setTaskId] = useState<string | null>(null);

    const queryClient = useQueryClient();

    const uploadMutation = useMutation({
        mutationFn: (file: File) => uploadFile(file),
        onSuccess: (response) => {
            if (response.status === 'success') {
                setTaskId(response.data.taskId);
                setdatasetId(response.data.datasetId);
            } else {
                toast.error(`Upload failed: ${response.message}`);
            }
        }
    })

    const updateTypeMutation = useMutation({
        mutationFn: ({ columnId, datasetId, newType }: { columnId: string, datasetId: string, newType: string }) =>
            updateColumnType(columnId, datasetId, newType),
        onSuccess: (response) => {
            queryClient.invalidateQueries({ queryKey: ['dataset'] });
            if (response.status === 'success') {
                setTaskId(response.data.taskId);
                toast.success(`Column type conversion started`);
            } else {
                toast.error(`Type conversion failed: ${response.message}`);
            }
        },
        onError: (error: any) => {
            const errorMessage = error.response?.data?.message || 'Failed to update column type';
            toast.error(errorMessage);
        }
    });

    const dataQuery = useQuery({
        queryKey: ['dataset', datasetId, currentPage],
        queryFn: async () => {
            try {
                return await getDatasetDetails(datasetId, currentPage);
            } catch (error) {
                if (error instanceof ValidationError || error instanceof ApiError) {
                    throw error;
                }
                console.error('Unexpected error while fetching dataset:', error);
                throw new ApiError('An unexpected error occurred while fetching dataset', 500);
            }
        },
        enabled: false
    });

    useEffect(() => {
        const fetchPageData = async () => {
            if (datasetId && !isLoading) {
                try {
                    const dataResponse = await dataQuery.refetch();
                    
                    if (dataResponse.data?.status === 'success') {
                        const responseData = dataResponse.data.data;
                        setData({
                            column: responseData.columns,
                            dataRows: responseData.rows,
                            pagination: {
                                currentPage: dataResponse.data.pagination.current_page,
                                totalPages: dataResponse.data.pagination.total_pages,
                                totalItems: dataResponse.data.pagination.count,
                                pageSize: dataResponse.data.pagination.page_size
                            }
                        });
                    } else {
                        toast.error('Failed to fetch page data');
                    }
                } catch (error) {
                    console.error('Error fetching page data:', error);
                    toast.error('Error loading page data');
                }
            }
        };
    
        fetchPageData();
    }, [currentPage]);


    useEffect(() => {
        let intervalId: number;
        setData(null);

        if (taskId && datasetId) {
            setIsLoading(true);
            intervalId = window.setInterval(async () => {
                try {
                    const response = await getTaskStatus(datasetId, taskId);
                    const status: TaskStatus = response.data;
                    setProgress(status.progress);

                    if (status.status === 'SUCCESS') {
                        clearInterval(intervalId);
                        const dataResponse = await dataQuery.refetch();

                        if (dataResponse.data?.status === 'success') {
                            const responseData = dataResponse.data.data;
                            setData({
                                column: responseData.columns,
                                dataRows: responseData.rows,
                                pagination: {
                                    currentPage: dataResponse.data.pagination.current_page,
                                    totalPages: dataResponse.data.pagination.total_pages,
                                    totalItems: dataResponse.data.pagination.count,
                                    pageSize: dataResponse.data.pagination.page_size
                                }
                            });
                            toast.success('File processing completed');
                            setIsLoading(false);
                        } else {
                            toast.error('Error loading data');
                            setIsLoading(false);
                        }
                    } else if (status.status === 'FAILED') {
                        clearInterval(intervalId);
                        toast.error('File processing failed');
                        setIsLoading(false);
                    }
                } catch (error) {
                    clearInterval(intervalId);
                    toast.error('Error checking processing status');
                    setIsLoading(false);
                }
            }, 3000);
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [taskId, datasetId]);

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
        if (customInferredTypes && datasetId) {
            setProgress(0);
            await updateTypeMutation.mutateAsync({
                columnId: customInferredTypes.column.id,
                datasetId: datasetId,
                newType: customInferredTypes.newType
            });
            setCustomInferredTypes(null);
        }
    };

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
        />
    );
};