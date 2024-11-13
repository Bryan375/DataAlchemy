import {FC} from 'react';
import {ProcessingProgressProps} from "../../../types/DataInference/dataInference.types.ts";
import {Progress} from "../../ui/progress.tsx";


export const ProcessingProgress: FC<ProcessingProgressProps> = ({progress}) => {
    return (
        <div className={'mb-6'}>
            <div className={'flex justify-between mb-2'}>
                <span className={'text-sm font-medium text-blue-600'}>Inferring data types...</span>
                <span className={'text-sm font-medium text-blue-600'}>{progress}%</span>
            </div>
            <Progress value={progress} className={'w-full h-2'}/>
        </div>
    );
};

