import {FC, useState} from "react";
import {TypeChangeDialogProps} from "../../../types/DataInference/dataInference.types.ts";
import {Column} from "../../../models/DataInference/dataInference.models.ts.tsx";
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "../../ui/dialog.tsx";
import {Button} from "../../ui/button.tsx";
import {DataTypeSelector} from "../../molecules/DataInference/DataTypeSelector.tsx";


export const TypeChangeDialog: FC<TypeChangeDialogProps> = ({ column, currentType, onTypeChange, onApplyChanges }) => {
    const [isOpen, setIsOpen] = useState(false);

    const handleTypeChange = (column: Column) => (newType: string | null) => {
        onTypeChange(column, newType);
    };

    const handleOpenChange = (open: boolean) => {
        setIsOpen(open);
        if (!open) {
            onTypeChange(column, null)
        }
    }

    const handleApplyChanges = (): void => {
        onApplyChanges();
        setIsOpen(false);
    }

    return (
        <Dialog open={isOpen} onOpenChange={handleOpenChange}>
            <DialogTrigger asChild>
                <Button variant="outline" className={'border-blue-200 text-blue-600 hover:bg-blue-50'}>
                    {currentType}
                </Button>
            </DialogTrigger>
            <DialogContent className={'sm:max-w-[425px]'}>
                <DialogHeader>
                    <DialogTitle className={'text-blue-600'}>Change Data Type</DialogTitle>
                    <DialogDescription>
                        Select a new data type for the column {column.name}
                    </DialogDescription>
                </DialogHeader>
                <DataTypeSelector onTypeChange={handleTypeChange(column)} />
                <DialogFooter>
                    <Button onClick={handleApplyChanges} className={'bg-blue-600 hover:bg-blue-700 text-white'}>
                        Apply Changes
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>

    )
}