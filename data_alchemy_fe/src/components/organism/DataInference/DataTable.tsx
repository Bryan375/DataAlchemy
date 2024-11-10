import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";
import {FC} from "react";
import {DataTableProps} from "@/types/DataInference/dataInference.types.ts";
import {Pagination} from "@/components/molecules/DataInference/Pagination.tsx";


export const DataTable: FC<DataTableProps> = ({ data, columns, pagination, currentPage, onPageChange }) => {
    return (
        <>
            <div className="rounded-md border border-blue-200 overflow-x-auto">
                <Table>
                    <TableHeader>
                        <TableRow>
                            {columns.map((column) => (
                                <TableHead key={column.name}>{column.name}</TableHead>
                            ))}
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {data.map((row, index) => (
                            <TableRow key={index}>
                                {columns.map((column) => (
                                    <TableCell key={column.name}>{row[column.name]}</TableCell>
                                ))}
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
            <Pagination
                currentPage={currentPage}
                totalPages={pagination.totalPages}
                onPageChange={onPageChange}
            />
        </>
    )
}