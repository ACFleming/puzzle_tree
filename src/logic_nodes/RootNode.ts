/**
 * RootNode.ts
 *
 * Root node. The entry point of the graph.
 * State is set manually by the user rather than calculated from inputs.
 * A graph may have multiple roots.
 * Accepts no inputs.
 */

import { LogicObj } from "./LogicObj";
import { NodeType } from "./nodeType";

export class RootNode extends LogicObj {
    readonly nodeType = NodeType.ROOT;

    /** Roots accept no inputs — this is a no-op. */
    override addInput(_i: LogicObj): void {}

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
