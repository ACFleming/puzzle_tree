/**
 * nodeType.ts
 *
 * Discriminant type used to identify each node/edge variant in the graph.
 */

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
