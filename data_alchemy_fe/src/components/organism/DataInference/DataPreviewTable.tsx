import {FC} from "react";
import {Column, DataPreviewTableProps, PreviewData} from "@/types/DataInference/dataInference.ts";
import {Table, TableBody, TableCell, TableHead, TableHeader, TableRow} from "@/components/ui/table.tsx";

export const DataPreviewTable: FC<DataPreviewTableProps> = ({ columnDetails, previewData }) => {
    return (
      <div className={'rounded-md border border-blue-200 overflow-x-auto'}>
          <Table>
              <TableHeader className={'bg-blue-50'}>
                  <TableRow>
                      {columnDetails.map((column: Column) => (
                            <TableHead key={column.name}>{column.name}</TableHead>
                      ))}
                  </TableRow>
              </TableHeader>
              <TableBody>
                  {previewData.map((row: PreviewData, index: number) => (
                      <TableRow key={index}>
                          {columnDetails.map((column: Column) => (
                              <TableCell key={column.name}>{row[column.name]}</TableCell>
                          ))}
                      </TableRow>
                  ))}
              </TableBody>
          </Table>
      </div>
    );
}