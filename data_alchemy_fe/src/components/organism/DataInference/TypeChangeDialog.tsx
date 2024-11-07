import {TypeChangeDialogProps} from "@/types/DataInference/dataInference.ts";
import {FC} from "react";
import {
    Dialog,
    DialogContent,
    DialogDescription, DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog.tsx";
import {Button} from "@/components/ui/button.tsx";
import {DataPreviewTable} from "@/components/organism/DataInference/DataPreviewTable.tsx";
import {DataTypeSelector} from "@/components/molecules/DataInference/DataTypeSelector.tsx";


export const TypeChangeDialog: FC<TypeChangeDialogProps> = ({ column, currentType, onTypeChange, previewChanges, onApplyChanges }) => {
    const handleTypeChange = (columnName: string) => (newType: string) => {
        onTypeChange(columnName, newType);
    };

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button variant="outline" className={'border-blue-200 text-blue-600 hover:bg-blue-50'}>
                    {currentType}
                </Button>
            </DialogTrigger>
            <DialogContent className={'sm:max-w-[425px]'}>
                <DialogHeader>
                    <DialogTitle className={'text-blue-600'}>Change Data Type</DialogTitle>
                    <DialogDescription>
                        Select a new data type for the column
                    </DialogDescription>
                </DialogHeader>
                <DataTypeSelector onTypeChange={handleTypeChange} />
                {previewChanges && (
                    <div className={'mt-4'}>
                        <h4 className={'mb-2 font-semibold text-blue-600'}>Preview of changes:</h4>
                        <DataPreviewTable
                            columnDetails={[{name: column.name, inferredType: column.inferredType, userType: column.userType}]}
                            previewData={[{previewData: previewChanges.newType}]}
                        />
                    </div>
                )}
                <DialogFooter>
                    <Button onClick={onApplyChanges} className={'bg-blue-600 hover:bg-blue-700 text-white'}>
                        Apply Changes
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>

    )
}