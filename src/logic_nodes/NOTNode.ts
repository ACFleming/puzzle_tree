/**
 * NOTNode.ts
 *
 * NOT gate. State is the inverse of its single input.
 * Accepts exactly 1 input and 1 output.
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class NOTNode extends LogicObj {
    readonly nodeType = NodeType.NOT;

    /** Enforces max 1 input. */
    override addInput(i: LogicObj): void {
        this._inputObjs = [i];
    }

    /** Enforces max 1 output. */
    override addOutput(o: LogicObj): void {
        this._outputObjs = [o];
    }

    /** True if the single input is false, and vice versa. */
    override calculateState(): void {
        if (this._inputObjs.length === 0) this._state = false;
        this._state = !this._inputObjs[0].state;
    }
}
