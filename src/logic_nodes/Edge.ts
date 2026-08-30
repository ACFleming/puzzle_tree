/**
 * Edge.ts
 *
 * Connects two non-Edge nodes together.
 * An Edge can have at most 1 input and 1 output.
 *
 * Edges have a selected state controlled by SwitchNode.
 * When not selected, state does not propagate (always false).
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class Edge extends LogicObj {
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
    override addInput(i: LogicObj): void {
        this._inputObjs = [i];
    }

    /** Enforces max 1 output. */
    override addOutput(o: LogicObj): void {
        this._outputObjs = [o];
    }

    /** State is true only if the input is true AND this edge is selected. */
    override calculateState(): void {
        if (this._inputObjs.length === 0) this._state = false;
        this._state = this._inputObjs[0].state && this._selected;
    }
}
