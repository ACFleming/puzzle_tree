/**
 * LogicObj.ts
 *
 * Abstract base class for all nodes and edges in the puzzle tree.
 * Each LogicObj has a boolean state that is calculated from its inputs,
 * and propagates that state to its outputs when updated.
 */

import { CONNECTIONS_LIMIT } from "./constants";
import { NodeType } from "./nodeType";

/** Module-level ID counter, incremented for each new LogicObj instance. */
let _idCounter = 0;

export abstract class LogicObj {
    /** Unique numeric ID for this instance. */
    readonly id: number;

    /**
     * Human-readable string ID used for debugging.
     * Format: ClassName_id, e.g. "ORNode_3".
     */
    readonly boolId: string;

    /** Discriminant identifying which node/edge variant this is. */
    abstract readonly nodeType: NodeType;

    /** The current boolean state of this node. */
    protected _state: boolean = false;

    /** Nodes/edges feeding into this node. */
    protected _inputObjs: LogicObj[] = [];

    /** Nodes/edges this node feeds into. */
    protected _outputObjs: LogicObj[] = [];

    constructor() {
        this.id = _idCounter++;
        this.boolId = `${this.constructor.name}_${this.id}`;
    }

    /** Returns the current boolean state of this node. */
    get state(): boolean {
        return this._state;
    }

    /**
     * Connects an input LogicObj to an output LogicObj via an Edge.
     * Exactly one of the two arguments must be an Edge.
     *
     * @param input - the upstream node or edge
     * @param output - the downstream node or edge
     */
    static connect(input: LogicObj, output: LogicObj): void {
        const inputIsEdge = input.nodeType == NodeType.EDGE;
        const outputIsEdge = output.nodeType == NodeType.EDGE;
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
     * @param output - the downstream LogicObj to add
     */
    addOutput(output: LogicObj): void {
        if (this._outputObjs.length < CONNECTIONS_LIMIT)
            this._outputObjs.push(output);
    }

    /**
     * Adds an input connection. Subclasses may override to enforce max connections.
     * @param input - the upstream LogicObj to add
     */
    addInput(input: LogicObj): void {
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
