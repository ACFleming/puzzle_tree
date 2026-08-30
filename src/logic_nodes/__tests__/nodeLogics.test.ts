import { describe, it, expect } from "vitest";
import {
    LogicObj,
    Edge,
    RootNode,
    LeafNode,
    ORNode,
    ANDNode,
    NOTNode,
    SwitchNode,
} from "../index";

// ── helpers ───────────────────────────────────────────────────────────────────

/** Wire: Root → Edge → Node → Edge → Leaf and return all parts */
function makeChain(middle: LogicObj) {
    const root = new RootNode();
    const e1 = new Edge();
    const e2 = new Edge();
    const leaf = new LeafNode();
    LogicObj.connect(root, e1);
    LogicObj.connect(e1, middle);
    LogicObj.connect(middle, e2);
    LogicObj.connect(e2, leaf);
    return { root, e1, middle, e2, leaf };
}

// ── RootNode ──────────────────────────────────────────────────────────────────

describe("RootNode", () => {
    it("starts false", () => {
        const r = new RootNode();
        expect(r.state).toBe(false);
    });

    it("on() sets state true", () => {
        const r = new RootNode();
        r.on();
        expect(r.state).toBe(true);
    });

    it("off() sets state false", () => {
        const r = new RootNode();
        r.on();
        r.off();
        expect(r.state).toBe(false);
    });

    it("accepts no inputs", () => {
        const r = new RootNode();
        const e = new Edge();
        r.addInput(e);
        expect(r.state).toBe(false);
    });
});

// ── Edge ──────────────────────────────────────────────────────────────────────

describe("Edge", () => {
    it("propagates true state from input", () => {
        const root = new RootNode();
        const edge = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(root, edge);
        LogicObj.connect(edge, leaf);
        root.on();
        expect(edge.state).toBe(true);
    });

    it("blocks state when not selected", () => {
        const root = new RootNode();
        const edge = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(root, edge);
        LogicObj.connect(edge, leaf);
        edge.setSelected(false);
        root.on();
        expect(edge.state).toBe(false);
        expect(leaf.state).toBe(false);
    });

    it("only keeps 1 input", () => {
        const edge = new Edge();
        const r1 = new RootNode();
        const r2 = new RootNode();
        edge.addInput(r1);
        edge.addInput(r2);
        // second addInput replaces first
        expect((edge as any)._inputObjs.length).toBe(1);
    });
});

// ── ORNode ────────────────────────────────────────────────────────────────────

describe("ORNode", () => {
    it("false when no inputs true", () => {
        const { root, leaf } = makeChain(new ORNode());
        root.off();
        expect(leaf.state).toBe(false);
    });

    it("true when one input true", () => {
        const { root, leaf } = makeChain(new ORNode());
        root.on();
        expect(leaf.state).toBe(true);
    });

    it("true when all inputs true", () => {
        const or = new ORNode();
        const r1 = new RootNode();
        const r2 = new RootNode();
        const e1 = new Edge();
        const e2 = new Edge();
        const e3 = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(r1, e1);
        LogicObj.connect(r2, e2);
        LogicObj.connect(e1, or);
        LogicObj.connect(e2, or);
        LogicObj.connect(or, e3);
        LogicObj.connect(e3, leaf);
        r1.on();
        r2.on();
        expect(leaf.state).toBe(true);
    });

    it("true when only one of two inputs true", () => {
        const or = new ORNode();
        const r1 = new RootNode();
        const r2 = new RootNode();
        const e1 = new Edge();
        const e2 = new Edge();
        const e3 = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(r1, e1);
        LogicObj.connect(r2, e2);
        LogicObj.connect(e1, or);
        LogicObj.connect(e2, or);
        LogicObj.connect(or, e3);
        LogicObj.connect(e3, leaf);
        r1.on();
        r2.off();
        expect(leaf.state).toBe(true);
    });
});

// ── ANDNode ───────────────────────────────────────────────────────────────────

describe("ANDNode", () => {
    it("false when no inputs", () => {
        const and = new ANDNode();
        and.calculateState();
        expect(and.state).toBe(false);
    });

    it("false when one of two inputs false", () => {
        const and = new ANDNode();
        const r1 = new RootNode();
        const r2 = new RootNode();
        const e1 = new Edge();
        const e2 = new Edge();
        const e3 = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(r1, e1);
        LogicObj.connect(r2, e2);
        LogicObj.connect(e1, and);
        LogicObj.connect(e2, and);
        LogicObj.connect(and, e3);
        LogicObj.connect(e3, leaf);
        r1.on();
        r2.off();
        expect(leaf.state).toBe(false);
    });

    it("true when all inputs true", () => {
        const and = new ANDNode();
        const r1 = new RootNode();
        const r2 = new RootNode();
        const e1 = new Edge();
        const e2 = new Edge();
        const e3 = new Edge();
        const leaf = new LeafNode();
        LogicObj.connect(r1, e1);
        LogicObj.connect(r2, e2);
        LogicObj.connect(e1, and);
        LogicObj.connect(e2, and);
        LogicObj.connect(and, e3);
        LogicObj.connect(e3, leaf);
        r1.on();
        r2.on();
        expect(leaf.state).toBe(true);
    });
});

// ── NOTNode ───────────────────────────────────────────────────────────────────

describe("NOTNode", () => {
    it("true when input false", () => {
        const { root, leaf } = makeChain(new NOTNode());
        root.off();
        expect(leaf.state).toBe(true);
    });

    it("false when input true", () => {
        const { root, leaf } = makeChain(new NOTNode());
        root.on();
        expect(leaf.state).toBe(false);
    });
});

// ── SwitchNode ────────────────────────────────────────────────────────────────

describe("SwitchNode", () => {
    function makeSwitch() {
        const root = new RootNode();
        const eIn = new Edge();
        const sw = new SwitchNode();
        const eOut1 = new Edge();
        const eOut2 = new Edge();
        const leaf1 = new LeafNode();
        const leaf2 = new LeafNode();
        LogicObj.connect(root, eIn);
        LogicObj.connect(eIn, sw);
        LogicObj.connect(sw, eOut1);
        LogicObj.connect(sw, eOut2);
        LogicObj.connect(eOut1, leaf1);
        LogicObj.connect(eOut2, leaf2);
        return { root, sw, eOut1, eOut2, leaf1, leaf2 };
    }

    it("output edges start unselected", () => {
        const { root, leaf1, leaf2 } = makeSwitch();
        root.on();
        expect(leaf1.state).toBe(false);
        expect(leaf2.state).toBe(false);
    });

    it("selecting an edge propagates state", () => {
        const { root, sw, eOut1, leaf1, leaf2 } = makeSwitch();
        root.on();
        sw.selectEdges(new Map([[eOut1, true]]));
        eOut1.update();
        expect(leaf1.state).toBe(true);
        expect(leaf2.state).toBe(false);
    });

    it("switch state true when input true", () => {
        const { root, sw } = makeSwitch();
        root.on();
        expect(sw.state).toBe(true);
    });

    it("throws on unknown edge", () => {
        const { sw } = makeSwitch();
        const stranger = new Edge();
        expect(() => sw.selectEdges(new Map([[stranger, true]]))).toThrow();
    });

    it("toString shows edge selection state", () => {
        const { sw, eOut1, eOut2 } = makeSwitch();
        const str = sw.toString();
        expect(str).toContain(eOut1.boolId);
        expect(str).toContain(eOut2.boolId);
        expect(str).toContain("false");
    });
});

// ── LeafNode ──────────────────────────────────────────────────────────────────

describe("LeafNode", () => {
    it("starts false", () => {
        const leaf = new LeafNode();
        expect(leaf.state).toBe(false);
    });

    it("true when input true", () => {
        const { root, leaf } = makeChain(new ORNode());
        root.on();
        expect(leaf.state).toBe(true);
    });

    it("false when input false", () => {
        const { root, leaf } = makeChain(new ORNode());
        root.off();
        expect(leaf.state).toBe(false);
    });
});

// ── propagation ───────────────────────────────────────────────────────────────

describe("state propagation", () => {
    it("propagates through a multi-node chain", () => {
        // Root → Edge → OR → Edge → AND → Edge → Leaf
        const root = new RootNode();
        const r2 = new RootNode();
        const or = new ORNode();
        const and = new ANDNode();
        const leaf = new LeafNode();
        const e1 = new Edge(),
            e2 = new Edge();
        const e3 = new Edge(),
            e4 = new Edge();

        LogicObj.connect(root, e1);
        LogicObj.connect(e1, or);
        LogicObj.connect(or, e2);
        LogicObj.connect(e2, and);
        LogicObj.connect(r2, e3);
        LogicObj.connect(e3, and);
        LogicObj.connect(and, e4);
        LogicObj.connect(e4, leaf);

        root.on();
        r2.on();
        expect(leaf.state).toBe(true);

        r2.off();
        expect(leaf.state).toBe(false);
    });

    it("toggling root updates leaf immediately", () => {
        const { root, leaf } = makeChain(new ORNode());
        root.on();
        expect(leaf.state).toBe(true);
        root.off();
        expect(leaf.state).toBe(false);
        root.on();
        expect(leaf.state).toBe(true);
    });
});
