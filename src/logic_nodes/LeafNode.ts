/**
 * LeafNode.ts
 *
 * Leaf node. The terminal end of the graph.
 * State is true if its single input edge is true.
 * Accepts exactly 1 input, no outputs.
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class LeafNode extends LogicObj {
    readonly nodeType = NodeType.LEAF;

    /** Enforces max 1 input. */
    override addInput(i: LogicObj): void {
        this._inputObjs = [i];
    }

    /** Leaves have no outputs — this is a no-op. */
    override addOutput(_o: LogicObj): void {}

    /** True if the single input is true. */
    override calculateState(): void {
        this._state = this._inputObjs.some((o) => o.state);
    }
}
