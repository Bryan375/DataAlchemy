import {FC} from "react";
import {DataTypeSelectorProps} from "@/types/DataInference/dataInference.ts";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";

export const DataTypeSelector: FC<DataTypeSelectorProps> = ({onTypeChange}) => {
    return (
        <Select onValueChange={onTypeChange}>
            <SelectTrigger className="w-[180px] border-blue-200">
                <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="int64">Integer</SelectItem>
                <SelectItem value="float64">Float</SelectItem>
                <SelectItem value="object">Text</SelectItem>
                <SelectItem value="datetime64">Date</SelectItem>
                <SelectItem value="bool">Boolean</SelectItem>
                <SelectItem value="category">Category</SelectItem>
            </SelectContent>
        </Select>
    );
}