import { useCallback } from "react";
import {
    ReactFlow,
    ConnectionMode,
    MarkerType,
    type Connection,
    type NodeChange,
    type EdgeChange,
    type IsValidConnection,
} from "@xyflow/react";
import type { FlowNode, FlowEdge } from "./types";
import { useGraphStore } from "./graphStore";
import Toolbar from "./Toolbar";
import RootNodeComponent from "./nodes/RootNodeComponent";
import ORNodeComponent from "./nodes/ORNodeComponent";
import ANDNodeComponent from "./nodes/ANDNodeComponent";
import NOTNodeComponent from "./nodes/NOTNodeComponent";
import SwitchNodeComponent from "./nodes/SwitchNodeComponent";
import LeafNodeComponent from "./nodes/LeafNodeComponent";

const defaultEdgeOptions = {
    animated: false,
    markerEnd: {
        type: MarkerType.ArrowClosed,
        width: 20,
        height: 20,
        color: "#94a3b8",
    },
    style: {
        strokeWidth: 2,
        stroke: "#94a3b8",
    },
};

/**
 * Maps nodeType strings to their React components.
 * Defined outside the component or wrapped in useMemo to avoid
 * React Flow re-registering them on every render.
 */
const nodeTypes = {
    RootNode: RootNodeComponent,
    ORNode: ORNodeComponent,
    ANDNode: ANDNodeComponent,
    NOTNode: NOTNodeComponent,
    SwitchNode: SwitchNodeComponent,
    LeafNode: LeafNodeComponent,
};

export default function PuzzleGraph() {
    const nodes = useGraphStore((s) => s.nodes);
    const edges = useGraphStore((s) => s.edges);
    const onNodesChange = useGraphStore((s) => s.onNodesChange);
    const onEdgesChange = useGraphStore((s) => s.onEdgesChange);
    const connectNodes = useGraphStore((s) => s.connectNodes);
    const removeNode = useGraphStore((s) => s.removeNode);
    const removeEdge = useGraphStore((s) => s.removeEdge);

    const handleNodesChange = (changes: NodeChange<FlowNode>[]) => {
        changes.forEach((change) => {
            if (change.type === "remove") removeNode(Number(change.id));
        });
        onNodesChange(changes.filter((c) => c.type !== "remove"));
    };

    const handleEdgesChange = (changes: EdgeChange<FlowEdge>[]) => {
        changes.forEach((change) => {
            if (change.type === "remove") removeEdge(change.id);
        });
        onEdgesChange(changes.filter((c) => c.type !== "remove"));
    };

    // const handleNodesChange = useCallback(
    //     (changes: NodeChange<FlowNode>[]) => {
    //         changes.forEach((change) => {
    //             if (change.type === "remove") removeNode(Number(change.id));
    //         });
    //         onNodesChange(changes.filter((c) => c.type !== "remove"));
    //     },
    //     [onNodesChange, removeNode],
    // );

    // const handleEdgesChange = useCallback(
    //     (changes: EdgeChange<FlowEdge>[]) => {
    //         changes.forEach((change) => {
    //             if (change.type === "remove") removeEdge(change.id);
    //         });
    //         onEdgesChange(changes.filter((c) => c.type !== "remove"));
    //     },
    //     [onEdgesChange, removeEdge],
    // );

    const isValidConnection: IsValidConnection<FlowEdge> = useCallback(
        (connection) => {
            const targetId = connection.target;
            const targetNode = nodes.find((n) => n.id === targetId);
            if (!targetNode) return false;

            const nodeType = targetNode.data.nodeType;

            const singleInputTypes = ["LeafNode", "SwitchNode", "NOTNode"];
            if (singleInputTypes.includes(nodeType)) {
                const existingInputs = edges.filter(
                    (e) => e.target === targetId,
                );
                if (existingInputs.length >= 1) return false;
            }

            if (connection.source === connection.target) return false;

            return true;
        },
        [nodes, edges],
    );

    /**
     * Called when the user drags a connection between two nodes on the canvas.
     * We extract the source and target model IDs from the node IDs and
     * call connectNodes on the store.
     */
    const onConnect = useCallback(
        (connection: Connection) => {
            const sourceModelId = Number(connection.source);
            const targetModelId = Number(connection.target);
            connectNodes(sourceModelId, targetModelId);
        },
        [connectNodes],
    );

    // inside PuzzleGraph, update the return:
    return (
        <div style={{ width: "100%", height: "100vh", position: "relative" }}>
            <Toolbar />
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                connectionMode={ConnectionMode.Loose}
                defaultEdgeOptions={defaultEdgeOptions}
                isValidConnection={isValidConnection}
                onNodesChange={handleNodesChange}
                onEdgesChange={handleEdgesChange}
                fitView
            />
        </div>
    );
}
