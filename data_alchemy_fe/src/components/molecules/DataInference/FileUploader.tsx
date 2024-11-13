import {FC} from "react";

import {FileUp, RefreshCw} from "lucide-react";
import {DataInferenceFileUploaderProps} from "../../../types/DataInference/dataInference.types.ts";
import {Input} from "../../ui/input.tsx";
import {Button} from "../../ui/button.tsx";

export const FileUploader: FC<DataInferenceFileUploaderProps> = ({onFileSelect, file, isLoading, OnSubmit}) => {
    return (
        <div className={'flex items-center space-x-4 mb-6'}>
            <Input
                type='file'
                onChange={onFileSelect}
                disabled={isLoading}
                accept={'.csv, .xlsx, .xls'}
                className={'flex-grow items-center'}
            />
            <Button
                onClick={OnSubmit}
                disabled={!file || isLoading}
                className={'bg-blue-600 hover:bg-blue-700 text-white'}
            >
                {isLoading ? <RefreshCw className={'mr-2 h-4 w-4 animate-spin'} /> : <FileUp className={'mr-2 h-4'}/> }
                {isLoading ? 'Processing...' : 'Submit'}
            </Button>
        </div>
    );
}