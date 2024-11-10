import {FC} from "react";
import {DataTypeSelectorProps} from "@/types/DataInference/dataInference.types.ts";
import {Select, SelectContent, SelectItem, SelectTrigger, SelectValue} from "@/components/ui/select.tsx";

export const DataTypeSelector: FC<DataTypeSelectorProps> = ({onTypeChange}) => {
    return (
        <Select onValueChange={onTypeChange}>
            <SelectTrigger className="w-[180px] border-blue-200">
                <SelectValue placeholder="Select type" />
            </SelectTrigger>
            <SelectContent>
                <SelectItem value="Integer">Integer</SelectItem>
                <SelectItem value="Decimal">Decimal</SelectItem>
                <SelectItem value="Text">Text</SelectItem>
                <SelectItem value="Datetime">Datetime</SelectItem>
                <SelectItem value="Boolean">Boolean</SelectItem>
                <SelectItem value="Category">Category</SelectItem>
            </SelectContent>
        </Select>
    );
}