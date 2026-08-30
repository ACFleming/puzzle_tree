import type { Node, Edge } from "@xyflow/react";

/**
 * Data payload attached to every React Flow node.
 * modelId links the canvas node back to its LogicObj instance.
 */
export type NodeData = {
    label: string;
    nodeType: string;
    state: boolean;
    modelId: number;
};

export type FlowNode = Node<NodeData>;

export type EdgeData = {
    selected: boolean;
};

export type FlowEdge = Edge<EdgeData>;
