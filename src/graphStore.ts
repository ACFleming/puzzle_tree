import { create } from "zustand";
import {
    applyNodeChanges,
    applyEdgeChanges,
    type NodeChange,
    type EdgeChange,
    useKeyPress,
} from "@xyflow/react";
import {
    StateObj,
    RootNode,
    ORNode,
    ANDNode,
    NOTNode,
    SwitchNode,
    LeafNode,
    Edge as ModelEdge,
} from "./nodeModel";
import type { FlowNode, FlowEdge, NodeData, EdgeData } from "./types";

// ── Store shape ───────────────────────────────────────────────────────────────

type GraphStore = {
    /** React Flow display data */
    nodes: FlowNode[];
    edges: FlowEdge[];

    /** Live model instances keyed by their numeric id */
    modelNodes: Map<number, StateObj>;
    modelEdges: Map<string, ModelEdge>;

    /** React Flow change handlers */
    onNodesChange: (changes: NodeChange<FlowNode>[]) => void;
    onEdgesChange: (changes: EdgeChange<FlowEdge>[]) => void;

    /** Graph actions */
    addNode: (nodeType: string, position: { x: number; y: number }) => void;
    removeNode: (modelId: number) => void;
    removeEdge: (edgeId: string) => void;
    connectNodes: (sourceModelId: number, targetModelId: number) => void;
    toggleRoot: (modelId: number) => void;
    selectEdge: (
        switchModelId: number,
        edgeModelId: string,
        selected: boolean,
    ) => void;

    /** Sync model state back to React Flow nodes */
    syncState: () => void;
};

// ── Helper ────────────────────────────────────────────────────────────────────

/**
 * Converts a StateObj instance into a React Flow node object.
 * Called when adding a node and when syncing state back to the canvas.
 */
function toFlowNode(
    model: StateObj,
    position: { x: number; y: number },
): FlowNode {
    return {
        id: String(model.id),
        type: model.constructor.name,
        position,
        data: {
            label: model.constructor.name,
            nodeType: model.constructor.name,
            state: model.state,
            modelId: model.id,
        },
    };
}

// ── Store ─────────────────────────────────────────────────────────────────────

export const useGraphStore = create<GraphStore>((set, get) => ({
    nodes: [],
    edges: [],
    modelNodes: new Map(),
    modelEdges: new Map(),

    onNodesChange: (changes: NodeChange<FlowNode>[]) => {
        set((s) => ({ nodes: applyNodeChanges<FlowNode>(changes, s.nodes) }));
    },

    onEdgesChange: (changes: EdgeChange<FlowEdge>[]) => {
        set((s) => ({ edges: applyEdgeChanges<FlowEdge>(changes, s.edges) }));
    },

    /**
     * Creates a new model node of the given type and adds it to the canvas.
     */
    addNode: (nodeType, position) => {
        const model = createModelNode(nodeType);
        if (!model) return;

        const flowNode = toFlowNode(model, position);

        set((s) => ({
            modelNodes: new Map(s.modelNodes).set(model.id, model),
            nodes: [...s.nodes, flowNode],
        }));
    },

    /**
     * Removes a node from the canvas and the model.
     * Also removes any edges connected to it.
     */
    removeNode: (modelId) => {
        const { modelEdges } = get();

        // find all edges connected to this node
        const edgeIdsToRemove = Array.from(modelEdges.keys()).filter(
            (edgeId) => {
                const flowEdge = get().edges.find((e) => e.id === edgeId);
                return (
                    flowEdge?.source === String(modelId) ||
                    flowEdge?.target === String(modelId)
                );
            },
        );

        set((s) => ({
            modelNodes: (() => {
                const next = new Map(s.modelNodes);
                next.delete(modelId);
                return next;
            })(),
            modelEdges: (() => {
                const next = new Map(s.modelEdges);
                edgeIdsToRemove.forEach((id) => next.delete(id));
                return next;
            })(),
            nodes: s.nodes.filter((n) => n.id !== String(modelId)),
            edges: s.edges.filter((e) => !edgeIdsToRemove.includes(e.id)),
        }));
    },

    /**
     * Removes an edge from the canvas and the model.
     */
    removeEdge: (edgeId) => {
        set((s) => ({
            modelEdges: (() => {
                const next = new Map(s.modelEdges);
                next.delete(edgeId);
                return next;
            })(),
            edges: s.edges.filter((e) => e.id !== edgeId),
        }));
        get().syncState();
    },

    /**
     * Connects two model nodes via a new Edge, and adds the visual edge
     * to the canvas. sourceModelId and targetModelId must both be non-Edge
     * nodes — the Edge is created automatically between them.
     */
    connectNodes: (sourceModelId, targetModelId) => {
        const { modelNodes, modelEdges } = get();
        const source = modelNodes.get(sourceModelId);
        const target = modelNodes.get(targetModelId);
        if (!source || !target) return;

        const edge = new ModelEdge();
        StateObj.connect(source, edge);
        StateObj.connect(edge, target);

        const edgeId = `e-${source.id}-${target.id}`;
        const isSwitchSource = source instanceof SwitchNode;
        const flowEdge: FlowEdge = {
            id: edgeId,
            source: String(source.id),
            target: String(target.id),
            data: { selected: !isSwitchSource },
        };

        set((s) => ({
            modelEdges: new Map(s.modelEdges).set(edgeId, edge),
            edges: [...s.edges, flowEdge],
        }));

        get().syncState();
    },

    /**
     * Toggles a RootNode between on and off, then syncs state to the canvas.
     */
    toggleRoot: (modelId) => {
        const { modelNodes } = get();
        const model = modelNodes.get(modelId);
        if (!(model instanceof RootNode)) return;
        model.setState(!model.state);
        get().syncState();
    },

    /**
     * Walks all model nodes and updates the React Flow node data to reflect
     * current boolean states. This is what causes nodes to change colour.
     */
    syncState: () => {
        const { modelNodes, modelEdges } = get();
        set((s) => ({
            nodes: s.nodes.map((flowNode) => {
                const model = modelNodes.get(Number(flowNode.id));
                if (!model) return flowNode;
                return {
                    ...flowNode,
                    data: { ...flowNode.data, state: model.state },
                };
            }),
            edges: s.edges.map((flowEdge) => {
                const model = modelEdges.get(flowEdge.id);
                if (!model) return flowEdge;
                const active = model.state;
                return {
                    ...flowEdge,
                    data: { selected: model.selected },
                    markerEnd: {
                        type: "arrowclosed",
                        width: 20,
                        height: 20,
                        color: active ? "#22c55e" : "#94a3b8",
                    },
                    style: {
                        strokeWidth: 2,
                        stroke: active ? "#22c55e" : "#94a3b8",
                    },
                };
            }),
        }));
    },

    /**
     * Toggles the selected state of a specific output edge on a SwitchNode.
     */
    selectEdge: (switchModelId, edgeModelId, selected) => {
        const { modelNodes, modelEdges } = get();
        const sw = modelNodes.get(switchModelId);
        const edge = modelEdges.get(edgeModelId);
        if (!(sw instanceof SwitchNode) || !(edge instanceof ModelEdge)) return;

        sw.selectEdges(new Map([[edge, selected]]));
        edge.update();
        get().syncState();
    },
}));

// ── Factory ───────────────────────────────────────────────────────────────────

/**
 * Creates the correct StateObj subclass for a given node type string.
 */
function createModelNode(nodeType: string): StateObj | null {
    switch (nodeType) {
        case "RootNode":
            return new RootNode();
        case "ORNode":
            return new ORNode();
        case "ANDNode":
            return new ANDNode();
        case "NOTNode":
            return new NOTNode();
        case "SwitchNode":
            return new SwitchNode();
        case "LeafNode":
            return new LeafNode();
        default:
            console.warn(`Unknown node type: ${nodeType}`);
            return null;
    }
}
