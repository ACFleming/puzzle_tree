/**
 * ANDNode.ts
 *
 * AND gate. State is true only if all input edges are true.
 * Accepts multiple inputs, one output.
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class ANDNode extends LogicObj {
    readonly nodeType = NodeType.AND;

    /** True only if all inputs are true (and at least one exists). */
    override calculateState(): void {
        this._state =
            this._inputObjs.length > 0 && this._inputObjs.every((o) => o.state);
    }
}
