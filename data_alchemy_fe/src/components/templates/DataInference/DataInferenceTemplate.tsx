import {FC} from 'react';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";
import {DataInferenceTemplateProps} from "@/types/DataInference/dataInference.ts";
import {FileUploader} from "@/components/molecules/DataInference/FileUploader.tsx";
import {ProcessingProgress} from "@/components/molecules/DataInference/ProcessingProgress.tsx";
import {Alert, AlertDescription, AlertTitle} from "@/components/ui/alert.tsx";
import {Tabs, TabsContent, TabsList, TabsTrigger} from "@/components/ui/tabs.tsx";
import {DataPreviewTable} from "@/components/organism/DataInference/DataPreviewTable.tsx";
import {DataTypesTable} from "@/components/organism/DataInference/DataTypesTable.tsx";


export const DataInferenceTemplate: FC<DataInferenceTemplateProps> = ({
  file,
  isLoading,
  progress,
  data,
  previewChanges,
  onFileSelect,
  onSubmit,
  onTypeChange,
  onApplyChanges,
  onDownload
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
                                    <TabsTrigger value="preview">Data Preview</TabsTrigger>
                                </TabsList>

                                <TabsContent value="types">
                                    {/*<DataPreviewTable*/}
                                    {/*    columnDetails={data.columnDetails}*/}
                                    {/*    previewData={data.previewData}*/}
                                    {/*/>*/}
                                    <DataTypesTable
                                        columnDetails={data.columnDetails}
                                        onTypeChange={onTypeChange}
                                        onApplyChanges={onApplyChanges}
                                        previewChanges={previewChanges}
                                    />
                                </TabsContent>

                                <TabsContent value="preview">
                                    <DataPreviewTable
                                        columnDetails={data.columnDetails}
                                        previewData={data.previewData}
                                    />
                                </TabsContent>
                            </Tabs>
                        </>
                    )}

                    {/* Alert */}
                    {/* Table for infer and preview data    */}
                    {/* Download button*/}

                </CardContent>
            </Card>
        </div>
    </div>);
};

