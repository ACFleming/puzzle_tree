import { create } from "zustand";
import {
    applyNodeChanges,
    applyEdgeChanges,
    type NodeChange,
    type EdgeChange,
    useKeyPress,
} from "@xyflow/react";
import {
    TreeObj,
    RootNode,
    ORNode,
    ANDNode,
    NOTNode,
    SwitchNode,
    LeafNode,
    Edge as TreeEdge,
} from "./nodeLogic";
import type { FlowNode, FlowEdge, NodeData, EdgeData } from "./types";

// ── Store shape ───────────────────────────────────────────────────────────────

type GraphStore = {
    /** React Flow display data */
    displayNodes: FlowNode[];
    displayEdges: FlowEdge[];

    /** Live tree instances keyed by their numeric id */
    treeNodes: Map<number, TreeObj>;
    treeEdges: Map<string, TreeEdge>;

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
 * Converts a TreeObj instance into a React Flow node object.
 * Called when adding a node and when syncing state back to the canvas.
 */
function toFlowNode(
    model: TreeObj,
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
    displayNodes: [],
    displayEdges: [],
    treeNodes: new Map(),
    treeEdges: new Map(),

    onNodesChange: (changes: NodeChange<FlowNode>[]) => {
        set((s) => ({ displayNodes: applyNodeChanges<FlowNode>(changes, s.displayNodes) }));
    },

    onEdgesChange: (changes: EdgeChange<FlowEdge>[]) => {
        set((s) => ({ displayEdges: applyEdgeChanges<FlowEdge>(changes, s.displayEdges) }));
    },

    /**
     * Creates a new model node of the given type and adds it to the canvas.
     */
    addNode: (nodeType, position) => {
        
        const logicNode = createLogicNode(nodeType);
       
        if (!logicNode) return;
        console.log(`HERE ${logicNode.id}`)
        const flowNode = toFlowNode(logicNode, position);
        console.log(`HERE ${flowNode.position.x}`)
        set((s) => ({
            treeNodes: new Map(s.treeNodes).set(logicNode.id, logicNode),
            displayNodes: [...s.displayNodes, flowNode],
        }));
    },

    /**
     * Removes a node from the canvas and the model.
     * Also removes any edges connected to it.
     */
    removeNode: (modelId) => {
        const { treeEdges } = get();

        // find all edges connected to this node
        const edgeIdsToRemove = Array.from(treeEdges.keys()).filter(
            (edgeId) => {
                const flowEdge = get().displayEdges.find((e) => e.id === edgeId);
                return (
                    flowEdge?.source === String(modelId) ||
                    flowEdge?.target === String(modelId)
                );
            },
        );

        set((s) => ({
            treeNodes: (() => {
                const next = new Map(s.treeNodes);
                next.delete(modelId);
                return next;
            })(),
            treeEdges: (() => {
                const next = new Map(s.treeEdges);
                edgeIdsToRemove.forEach((id) => next.delete(id));
                return next;
            })(),
            displayNodes: s.displayNodes.filter((n) => n.id !== String(modelId)),
            displayEdges: s.displayEdges.filter((e) => !edgeIdsToRemove.includes(e.id)),
        }));
    },

    /**
     * Removes an edge from the canvas and the model.
     */
    removeEdge: (edgeId) => {
        set((s) => ({
            treeEdges: (() => {
                const next = new Map(s.treeEdges);
                next.delete(edgeId);
                return next;
            })(),
            displayEdges: s.displayEdges.filter((e) => e.id !== edgeId),
        }));
        get().syncState();
    },

    /**
     * Connects two model nodes via a new Edge, and adds the visual edge
     * to the canvas. sourceModelId and targetModelId must both be non-Edge
     * nodes — the Edge is created automatically between them.
     */
    connectNodes: (sourceModelId, targetModelId) => {
        const { treeNodes, treeEdges } = get();
        const source = treeNodes.get(sourceModelId);
        const target = treeNodes.get(targetModelId);
        if (!source || !target) return;

        const edge = new TreeEdge();
        TreeObj.connect(source, edge);
        TreeObj.connect(edge, target);

        const edgeId = `${edge.boolId}-${source.id}-${target.id}`;
        const isSwitchSource = source instanceof SwitchNode;
        const flowEdge: FlowEdge = {
            id: edgeId,
            source: String(source.id),
            target: String(target.id),
            data: { selected: !isSwitchSource },
        };

        set((s) => ({
            treeEdges: new Map(s.treeEdges).set(edgeId, edge),
            displayEdges: [...s.displayEdges, flowEdge],
        }));

        get().syncState();
    },

    /**
     * Toggles a RootNode between on and off, then syncs state to the canvas.
     */
    toggleRoot: (modelId) => {
        const { treeNodes } = get();
        const model = treeNodes.get(modelId);
        if (!(model instanceof RootNode)) return;
        model.setState(!model.state);
        get().syncState();
    },

    /**
     * Walks all model nodes and updates the React Flow node data to reflect
     * current boolean states. This is what causes nodes to change colour.
     */
    syncState: () => {
        const { treeNodes, treeEdges } = get();
        set((s) => ({
            displayNodes: s.displayNodes.map((flowNode) => {
                const model = treeNodes.get(Number(flowNode.id));
                if (!model) return flowNode;
                return {
                    ...flowNode,
                    data: { ...flowNode.data, state: model.state },
                };
            }),
            displayEdges: s.displayEdges.map((flowEdge) => {
                const model = treeEdges.get(flowEdge.id);
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
        const { treeNodes, treeEdges } = get();
        const sw = treeNodes.get(switchModelId);
        const edge = treeEdges.get(edgeModelId);
        if (!(sw instanceof SwitchNode) || !(edge instanceof TreeEdge)) return;

        sw.selectEdges(new Map([[edge, selected]]));
        edge.update();
        get().syncState();
    },
}));

// ── Factory ───────────────────────────────────────────────────────────────────

/**
 * Creates the correct TreeObj subclass for a given node type string.
 */
function createLogicNode(nodeType: string): TreeObj | null {
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
