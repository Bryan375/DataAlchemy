import {FC} from "react";
import {DataTypesTableProps} from "../../../types/DataInference/dataInference.types.ts";
import {Column} from "../../../models/DataInference/dataInference.models.ts.tsx";
import {TypeChangeDialog} from "./TypeChangeDialog.tsx";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "../../ui/table.tsx";


export const DataTypesTable: FC<DataTypesTableProps> = ({columnDetails, onTypeChange, onApplyChanges}) => {
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
                            <TableCell className="text-gray-600">{column.customUserType}</TableCell>
                            <TableCell>
                                <TypeChangeDialog column={column} currentType={column.customUserType} onTypeChange={onTypeChange} onApplyChanges={onApplyChanges}/>
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}