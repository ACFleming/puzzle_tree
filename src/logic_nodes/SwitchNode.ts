/**
 * SwitchNode.ts
 *
 * Switch gate. Accepts one input, multiple output edges.
 * Its own state is true if its input is true (acts like OR with one input).
 *
 * Its primary role is controlling which of its output edges are selected
 * (active), allowing selective state propagation downstream.
 */

import { LogicObj } from "./LogicObj";
import { Edge } from "./Edge";
import { NodeType } from "./nodeType";

export class SwitchNode extends LogicObj {
    readonly nodeType = NodeType.SWITCH;

    /** Maps each output Edge to whether it is currently selected. */
    private _switchSelection: Map<Edge, boolean> = new Map();

    /** Enforces max 1 input. */
    override addInput(i: LogicObj): void {
        this._inputObjs = [i];
    }

    /**
     * Adds an output edge, defaulting it to unselected.
     * Only Edges may be outputs of a SwitchNode.
     */
    override addOutput(o: LogicObj): void {
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
