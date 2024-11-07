import {FC} from "react";
import {Column, DataTypesTableProps} from "@/types/DataInference/dataInference.ts";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import {TypeChangeDialog} from "@/components/organism/DataInference/TypeChangeDialog.tsx";

export const DataTypesTable: FC<DataTypesTableProps> = ({columnDetails, onTypeChange, onApplyChanges, previewChanges}) => {
    return (
        <div className={'rounded-md border border-blue-200 overflow-hidden'}>
            <Table>
                <TableHeader className={'bg-blue-50'}>
                    <TableRow>
                        <TableHead className={'w-[200px] text-blue-600'}>Column Name</TableHead>
                        <TableHead className={'text-blue-600'}>Inferred Type</TableHead>
                        <TableHead className={'text-blue-600'}>User-Defined Type</TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {columnDetails.map((column: Column) => (
                        <TableRow key={column.name} className="hover:bg-blue-50">
                            <TableCell className="font-medium text-blue-800">{column.name}</TableCell>
                            <TableCell className="text-gray-600">{column.inferredType}</TableCell>
                            <TableCell>
                                <TypeChangeDialog column={column} currentType={column.inferredType} onTypeChange={onTypeChange} onApplyChanges={onApplyChanges} previewChanges={previewChanges}/>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}