import {ChangeEvent, FC, useState} from 'react';
import {DataInferenceTemplate} from "@/components/templates/DataInference/DataInferenceTemplate.tsx";
import {DataState, PreviewChange} from "@/types/DataInference/dataInference.ts";

export const DataInference: FC = () => {
    const [file, setFile] = useState<File | null>(null);
    const [data, setData] = useState<DataState | null>(null);
    const [isLoading, setIsLoading] = useState<boolean>(false);
    const [progress, setProgress] = useState<number>(0);
    const [previewChanges, setPreviewChanges] = useState<PreviewChange | null>(null);

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
                    columnDetails: [
                        { name: 'id', inferredType: 'int64', userType: 'int64' },
                        { name: 'name', inferredType: 'object', userType: 'object' },
                        { name: 'date', inferredType: 'datetime64', userType: 'datetime64' },
                        { name: 'value', inferredType: 'float64', userType: 'float64' }
                    ],
                    previewData: [
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

    const fileUpload = (event: ChangeEvent<HTMLInputElement>) => {
        const files = event.target.files;
        if (files) {
            setFile(files[0]);
        }
    }


    return (
        <DataInferenceTemplate
            file={file}
            isLoading={isLoading}
            progress={progress}
            data={data}
            previewChanges={previewChanges}
            onFileSelect={fileUpload}
            onSubmit={handleSubmit}
            onTypeChange={(columnName: string, newType: string) => {}}
            onApplyChanges={() => {}}
            onDownload={() => {}}

        />
    );
};

