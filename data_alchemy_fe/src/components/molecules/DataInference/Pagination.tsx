import {FC} from "react";
import {ChevronLeft, ChevronRight} from "lucide-react";
import {Button} from "../../ui/button.tsx";
import {PaginationProps} from "../../../types/DataInference/dataInference.types.ts";

export const Pagination: FC<PaginationProps> = ({ currentPage, totalPages, onPageChange }) => {
    return (
        <div className="mt-4 flex justify-between items-center">
            <Button
                onClick={() => onPageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="bg-blue-600 hover:bg-blue-700 text-white"
            >
                <ChevronLeft className="h-4 w-4 mr-2"/>
                Previous
            </Button>
            <span className="text-sm text-blue-600">
                        Page {currentPage} of {totalPages}
                      </span>
            <Button
                onClick={() => onPageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="bg-blue-600 hover:bg-blue-700 text-white"
            >
                Next
                <ChevronRight className="h-4 w-4 ml-2"/>
            </Button>
        </div>
    )
}