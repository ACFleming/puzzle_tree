/**
 * ORNode.ts
 *
 * OR gate. State is true if one or more input edges are true.
 * Accepts multiple inputs, one output.
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class ORNode extends LogicObj {
    readonly nodeType = NodeType.OR;

    /** True if any input is true. */
    override calculateState(): void {
        this._state = this._inputObjs.some((o) => o.state);
    }
}
