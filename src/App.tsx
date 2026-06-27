import { ReactFlowProvider } from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import PuzzleGraph from "./PuzzleGraph";

export default function App() {
    return (
        <ReactFlowProvider>
            <PuzzleGraph />
        </ReactFlowProvider>
    );
}
