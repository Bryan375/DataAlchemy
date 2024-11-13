import {Toaster} from "react-hot-toast";
import {DataInference} from "./pages/DataInference";

function App() {
    return (
        <>
            <DataInference/>
            <Toaster
                position="top-center"
                toastOptions={{
                    duration: 4000,
                    style: {
                        background: '#fff',
                        color: '#363636',
                    },
                    success: {
                        duration: 3000,
                        style: {
                            background: '#10B981',
                            color: '#fff',
                        },
                    },
                    error: {
                        duration: 4000,
                        style: {
                            background: '#EF4444',
                            color: '#fff',
                        },
                    },
                }}
            />
        </>
    );
}


export default App
