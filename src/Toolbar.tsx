import { useGraphStore } from "./graphStore";

/** Node types the user can add, with display labels */
const NODE_TYPES = [
    { type: "RootNode", label: "Root" },
    { type: "ORNode", label: "OR" },
    { type: "ANDNode", label: "AND" },
    { type: "NOTNode", label: "NOT" },
    { type: "SwitchNode", label: "Switch" },
    { type: "LeafNode", label: "Leaf" },
];

export default function Toolbar() {
    const addNode = useGraphStore((s) => s.addNode);

    return (
        <div
            style={{
                position: "absolute",
                top: 16,
                left: 16,
                zIndex: 10,
                display: "flex",
                flexDirection: "column",
                gap: 8,
            }}
        >
            {NODE_TYPES.map(({ type, label }) => (
                <button
                    key={type}
                    onClick={() => addNode(type, { x: 200, y: 200 })}
                    style={{
                        padding: "6px 12px",
                        cursor: "pointer",
                    }}
                >
                    {label}
                </button>
            ))}
        </div>
    );
}
