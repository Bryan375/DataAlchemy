import {FC} from 'react';
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "@/components/ui/card.tsx";


export const DataInferenceTemplate: FC = () => {
    return (
        <div className={'min-h-screen bg-gradient-to-br from-blue-50 to-gray-100 py-8'}>
            <div className={'container mx-auto px-4 max-w-6xl'}>
                <Card className={'bg-white shadow-lg border-blue-200'}>
                    <CardHeader className={'bg-blue-600 text-white rounded-t-lg'}>
                        <CardTitle className={'text-2xl'}>DataAlchemy</CardTitle>
                        <CardDescription className={'text-blue-100'}>
                            Upload your CSV or Excel file to infer data types and preview data
                        </CardDescription>
                    </CardHeader>
                    <CardContent className={'p-6'}>
                    {/* File Upload and submit button */}
                    {/* Progress bar */}
                    {/* Alert */}
                    {/* Table for infer and preview data    */}
                    {/* Download button*/}

                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

