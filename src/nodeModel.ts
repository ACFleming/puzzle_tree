/**
 * node_model.ts
 *
 * Core logic for the puzzle_tree node graph.
 * Each node type represents a boolean logic gate. Nodes are connected via
 * Edges, and state propagates from RootNodes through the graph to LeafNodes.
 *
 * Typical graph shape:
 *   RootNode → Edge → [AND/OR/NOT/SwitchNode] → Edge → LeafNode
 */

const CONNECTIONS_LIMIT = 10;

// ── NodeType ──────────────────────────────────────────────────────────────────

/**
 * Discriminant values identifying each node type.
 * Used as const rather than enum to comply with erasableSyntaxOnly.
 */
export const NodeType = {
    ROOT: "ROOT",
    EDGE: "EDGE",
    LEAF: "LEAF",
    AND: "AND",
    OR: "OR",
    NOT: "NOT",
    SWITCH: "SWITCH",
} as const;

export type NodeType = (typeof NodeType)[keyof typeof NodeType];

// ── StateObj ──────────────────────────────────────────────────────────────────

/** Module-level ID counter, incremented for each new StateObj instance. */
let _idCounter = 0;

/**
 * Abstract base class for all nodes and edges in the graph.
 * Each StateObj has a boolean state that is calculated from its inputs,
 * and propagates that state to its outputs when updated.
 */
export abstract class StateObj {
    /** Unique numeric ID for this instance. */
    readonly id: number;

    /**
     * Human-readable string ID used for debugging.
     * Format: ClassName_id, e.g. "ORNode_3".
     */
    readonly boolId: string;

    /** The current boolean state of this node. */
    protected _state: boolean = false;

    /** Nodes/edges feeding into this node. */
    protected _inputObjs: StateObj[] = [];

    /** Nodes/edges this node feeds into. */
    protected _outputObjs: StateObj[] = [];

    constructor() {
        this.id = _idCounter++;
        this.boolId = `${this.constructor.name}_${this.id}`;
    }

    /** Returns the current boolean state of this node. */
    get state(): boolean {
        return this._state;
    }

    /**
     * Connects an input StateObj to an output StateObj via an Edge.
     * Exactly one of the two arguments must be an Edge.
     *
     * @param input - the upstream node or edge
     * @param output - the downstream node or edge
     */
    static connect(input: StateObj, output: StateObj): void {
        const inputIsEdge = input instanceof Edge;
        const outputIsEdge = output instanceof Edge;
        console.assert(
            inputIsEdge !== outputIsEdge,
            "Exactly one of input/output must be an Edge",
        );
        input.addOutput(output);
        output.addInput(input);
        input.update();
        output.update();
    }

    /**
     * Adds an output connection. Subclasses may override to enforce max connections.
     * @param output - the downstream StateObj to add
     */
    addOutput(output: StateObj): void {
        if (this._outputObjs.length < CONNECTIONS_LIMIT)
            this._outputObjs.push(output);
    }

    /**
     * Adds an input connection. Subclasses may override to enforce max connections.
     * @param input - the upstream StateObj to add
     */
    addInput(input: StateObj): void {
        if (this._inputObjs.length < CONNECTIONS_LIMIT)
            this._inputObjs.push(input);
    }

    /**
     * Recalculates this node's boolean state from its inputs.
     * Overridden by each subclass with its own logic (AND, OR, NOT, etc).
     */
    calculateState(): void {}

    /** Triggers an update on all downstream output nodes. */
    updateOutputs(): void {
        for (const out of this._outputObjs) out.update();
    }

    /**
     * Recalculates state then propagates to outputs.
     * This is the main propagation step called during graph evaluation.
     */
    update(): void {
        this.calculateState();
        this.updateOutputs();
    }

    toString(): string {
        return (
            `${this.boolId}:\n` +
            ` State: ${this._state}\n` +
            ` Inputs:  ${this._inputObjs.map((n) => n.boolId)}\n` +
            ` Outputs: ${this._outputObjs.map((n) => n.boolId)}`
        );
    }
}

// ── Edge ──────────────────────────────────────────────────────────────────────

/**
 * Connects two non-Edge nodes together.
 * An Edge can have at most 1 input and 1 output.
 *
 * Edges have a selected state controlled by SwitchNode.
 * When not selected, state does not propagate (always false).
 */
export class Edge extends StateObj {
    readonly nodeType = NodeType.EDGE;

    /** Whether this edge is active and will propagate state. */
    private _selected: boolean = true;

    /**
     * Sets whether this edge is selected (active).
     * Only SwitchNode should call this.
     * @param v - true to allow state propagation, false to block it
     */
    setSelected(v: boolean): void {
        this._selected = v;
    }

    get selected(): boolean {
        return this._selected;
    }

    /** Enforces max 1 input. */
    override addInput(i: StateObj): void {
        this._inputObjs = [i];
    }

    /** Enforces max 1 output. */
    override addOutput(o: StateObj): void {
        this._outputObjs = [o];
    }

    /** State is true only if the input is true AND this edge is selected. */
    override calculateState(): void {
        if (this._inputObjs.length === 0) this._state = false;
        this._state = this._inputObjs[0].state && this._selected;
    }
}

// ── ORNode ────────────────────────────────────────────────────────────────────

/**
 * OR gate. State is true if one or more input edges are true.
 * Accepts multiple inputs, one output.
 */
export class ORNode extends StateObj {
    readonly nodeType = NodeType.OR;

    /** True if any input is true. */
    override calculateState(): void {
        this._state = this._inputObjs.some((o) => o.state);
    }
}

// ── ANDNode ───────────────────────────────────────────────────────────────────

/**
 * AND gate. State is true only if all input edges are true.
 * Accepts multiple inputs, one output.
 */
export class ANDNode extends StateObj {
    readonly nodeType = NodeType.AND;

    /** True only if all inputs are true (and at least one exists). */
    override calculateState(): void {
        this._state =
            this._inputObjs.length > 0 && this._inputObjs.every((o) => o.state);
    }
}

// ── NOTNode ───────────────────────────────────────────────────────────────────

/**
 * NOT gate. State is the inverse of its single input.
 * Accepts exactly 1 input and 1 output.
 */
export class NOTNode extends StateObj {
    readonly nodeType = NodeType.NOT;

    /** Enforces max 1 input. */
    override addInput(i: StateObj): void {
        this._inputObjs = [i];
    }

    /** Enforces max 1 output. */
    override addOutput(o: StateObj): void {
        this._outputObjs = [o];
    }

    /** True if the single input is false, and vice versa. */
    override calculateState(): void {
        if (this._inputObjs.length === 0) this._state = false;
        this._state = !this._inputObjs[0].state;
    }
}

// ── SwitchNode ────────────────────────────────────────────────────────────────

/**
 * Switch gate. Accepts one input, multiple output edges.
 * Its own state is true if its input is true (acts like OR with one input).
 *
 * Its primary role is controlling which of its output edges are selected
 * (active), allowing selective state propagation downstream.
 */
export class SwitchNode extends StateObj {
    readonly nodeType = NodeType.SWITCH;

    /** Maps each output Edge to whether it is currently selected. */
    private _switchSelection: Map<Edge, boolean> = new Map();

    /** Enforces max 1 input. */
    override addInput(i: StateObj): void {
        this._inputObjs = [i];
    }

    /**
     * Adds an output edge, defaulting it to unselected.
     * Only Edges may be outputs of a SwitchNode.
     */
    override addOutput(o: StateObj): void {
        if (!(o instanceof Edge)) return;
        super.addOutput(o);
        o.setSelected(false);
        this._switchSelection.set(o, false);
    }

    /**
     * Sets the selected state for one or more output edges.
     * @param selections - map of Edge to desired selected state
     * @throws Error if an edge is not a known output of this switch
     */
    selectEdges(selections: Map<Edge, boolean>): void {
        for (const [edge, selected] of selections) {
            if (!this._switchSelection.has(edge))
                throw new Error(`Unknown edge on SwitchNode ${this.boolId}`);
            this._switchSelection.set(edge, selected);
            edge.setSelected(selected);
        }
    }

    /** True if the input is true. */
    override calculateState(): void {
        this._state = this._inputObjs.some((o) => o.state);
    }

    override toString(): string {
        const selections = Array.from(this._switchSelection.entries())
            .map(([edge, selected]) => `${edge.boolId}=${selected}`)
            .join(", ");
        return super.toString() + `\n Switch selections: ${selections}`;
    }
}

// ── RootNode ──────────────────────────────────────────────────────────────────

/**
 * Root node. The entry point of the graph.
 * State is set manually by the user rather than calculated from inputs.
 * A graph may have multiple roots.
 * Accepts no inputs.
 */
export class RootNode extends StateObj {
    readonly nodeType = NodeType.ROOT;

    /** Roots accept no inputs — this is a no-op. */
    override addInput(_i: StateObj): void {}

    /** State is set manually, not calculated. */
    override calculateState(): void {}

    /** Sets state to true and propagates. */
    on(): void {
        this.setState(true);
    }

    /** Sets state to false and propagates. */
    off(): void {
        this.setState(false);
    }

    /**
     * Sets state to the given value and propagates downstream.
     * @param bool_state - the new boolean state
     */
    setState(bool_state: boolean): void {
        this._state = bool_state;
        this.updateOutputs();
    }
}

// ── LeafNode ──────────────────────────────────────────────────────────────────

/**
 * Leaf node. The terminal end of the graph.
 * State is true if its single input edge is true.
 * Accepts exactly 1 input, no outputs.
 */
export class LeafNode extends StateObj {
    readonly nodeType = NodeType.LEAF;

    /** Enforces max 1 input. */
    override addInput(i: StateObj): void {
        this._inputObjs = [i];
    }

    /** Leaves have no outputs — this is a no-op. */
    override addOutput(_o: StateObj): void {}

    /** True if the single input is true. */
    override calculateState(): void {
        this._state = this._inputObjs.some((o) => o.state);
    }
}
