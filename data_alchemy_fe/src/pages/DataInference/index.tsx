import {ChangeEvent, FC, useState} from 'react';
import {DataInferenceTemplate} from "@/components/templates/DataInference/DataInferenceTemplate.tsx";
import {Column, CustomInferredTypes, Data} from "@/models/DataInference/dataInference.models.ts.tsx";

export const DataInference: FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [data, setData] = useState<Data | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [customInferredTypes, setCustomInferredTypes] = useState<CustomInferredTypes | null>(null);
    const [progress, setProgress] = useState<number>(0);
    const [currentPage, setCurrentPage] = useState<number>(1);
    const itemsPerPage = 50;

    const simulateProgress = (): void => {
        let progress: number = 0;
        const interval: NodeJS.Timeout = setInterval((): void => {
            progress += Math.random() * 10;
            if (progress > 100) progress = 100;
            setProgress(Math.round(progress));
            if (progress === 100) {
                clearInterval(interval);
                setIsLoading(false);
                setData({
                    column: [
                        { name: 'id', inferredType: 'int64', userType: 'int64' },
                        { name: 'name', inferredType: 'object', userType: 'object' },
                        { name: 'date', inferredType: 'datetime64', userType: 'datetime64' },
                        { name: 'value', inferredType: 'float64', userType: 'float64' }
                    ],
                    dataRows: [
                        { id: 1, name: 'John Doe', date: '2023-05-15', value: 100.5 },
                        { id: 2, name: 'Jane Smith', date: '2023-05-16', value: 200.75 },
                        { id: 3, name: 'Bob Johnson', date: '2023-05-17', value: 150.25 }
                    ]
                });
            }
        }, 200);
    };

    const handleSubmit = async (): Promise<void> => {
        setIsLoading(true)
        setProgress(0)
        setData(null)
        simulateProgress()
    }

    const fileUpload = (event: ChangeEvent<HTMLInputElement>): void => {
        const files = event.target.files;
        if (files) {
            setFile(files[0]);
        }
    }

    const onTypeChange = (column: Column, newType: string | null): void => {
        if (column && !newType) {
            console.log('closed');
            setCustomInferredTypes(null);
            console.log(customInferredTypes);
        }
        else if (newType && column.userType !== newType) {
            console.log(`changed for ${column.name} from ${column.userType} to ${newType}`);
            setCustomInferredTypes({ column, newType });
            console.log(customInferredTypes);
        }
    }

    const onApplyChange = (): void => {
        if (customInferredTypes) {
            setIsLoading(true)
            setProgress(0)
            setData(null)
            simulateProgress()
            setCustomInferredTypes(null);
        }
    }


    return (
        <DataInferenceTemplate
            file={file}
            isLoading={isLoading}
            progress={progress}
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

