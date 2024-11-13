import {FC} from 'react';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "../../ui/card.tsx";
import {DataInferenceTemplateProps} from "../../../types/DataInference/dataInference.types.ts";
import {FileUploader} from "../../molecules/DataInference/FileUploader.tsx";
import {ProcessingProgress} from "../../molecules/DataInference/ProcessingProgress.tsx";
import {Alert, AlertDescription, AlertTitle} from "../../ui/alert.tsx";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "../../ui/tabs.tsx";
import {DataTypesTable} from "../../organism/DataInference/DataTypesTable.tsx";
import {DataTable} from "../../organism/DataInference/DataTable.tsx";



export const DataInferenceTemplate: FC<DataInferenceTemplateProps> = ({
    file,
    isLoading,
    progress,
    data,
    onFileSelect,
    onSubmit,
    onTypeChange,
    onApplyChanges,
    currentPage,
    setCurrentPage
}) => {

    return (<div className={'min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 py-8'}>
        <div className={'container mx-auto px-4 max-w-6xl'}>
            <Card className={'bg-white shadow-lg border-blue-200'}>
                <CardHeader className={'bg-blue-600 text-white rounded-t-lg'}>
                    <CardTitle className={'text-2xl'}>DataAlchemy</CardTitle>
                    <CardDescription className={'text-blue-100'}>
                        Upload your CSV or Excel file to infer data types and preview data
                    </CardDescription>
                </CardHeader>
                <CardContent className={'p-6'}>
                    <FileUploader file={file} isLoading={isLoading} onFileSelect={onFileSelect} OnSubmit={onSubmit}/>

                    {isLoading && <ProcessingProgress progress={progress}/>}

                    {data && (
                        <>
                            <Alert className="mb-6 bg-green-50 border-green-200 text-green-800">
                                <AlertTitle className="text-green-800">Processing Complete</AlertTitle>
                                <AlertDescription className="text-green-700">
                                    Data types have been inferred. You can now review the types and preview the data.
                                </AlertDescription>
                            </Alert>


                            <Tabs defaultValue="types" className="mb-6">
                                <TabsList className="bg-blue-100 p-1 rounded-lg">
                                    <TabsTrigger value="types">Inferred Types</TabsTrigger>
                                    <TabsTrigger value="data">Data</TabsTrigger>
                                </TabsList>

                                <TabsContent value="types">
                                    <DataTypesTable
                                        columnDetails={data.column}
                                        onTypeChange={onTypeChange}
                                        onApplyChanges={onApplyChanges}
                                    />
                                </TabsContent>

                                <TabsContent value="data">
                                    <DataTable
                                        data={data.dataRows}
                                        columns={data.column}
                                        pagination={data.pagination}
                                        currentPage={currentPage}
                                        onPageChange={setCurrentPage}
                                    />
                                </TabsContent>
                            </Tabs>
                        </>
                    )}
                </CardContent>
            </Card>
        </div>
    </div>);
};

