import { useGraphStore } from "../graphStore";
import type { NodeData } from "../types";
import { Handle, Position } from "@xyflow/react";

export default function SwitchNodeComponent({
    data,
    id,
}: {
    data: NodeData;
    id: string;
}) {
    const selectEdge = useGraphStore((s) => s.selectEdge);
    const flowEdges = useGraphStore((s) => s.displayEdges);
    const state = data.state;

    /** Find all output edges from this switch node */
    const outputEdges = flowEdges.filter((e) => e.source === id);

    return (
        <div
            style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "2px solid",
                borderColor: state ? "#22c55e" : "#94a3b8",
                background: state ? "#dcfce7" : "#f1f5f9",
                minWidth: 100,
                textAlign: "center",
                transition: "all 0.15s ease",
            }}
        >
            <Handle type="target" position={Position.Left} />

            <div style={{ fontWeight: 600, fontSize: 13, marginBottom: 6 }}>
                Switch
            </div>

            <div
                style={{
                    fontSize: 11,
                    color: state ? "#16a34a" : "#64748b",
                    marginBottom: 8,
                }}
            >
                {state ? "TRUE" : "FALSE"}
            </div>

            {/** One toggle button per output edge */}
            {outputEdges.map((edge, i) => {
                const isSelected = edge.data?.selected ?? false;
                return (
                    <button
                        key={edge.id}
                        onClick={() =>
                            selectEdge(data.modelId, edge.id, !isSelected)
                        }
                        style={{
                            display: "block",
                            width: "100%",
                            marginBottom: 4,
                            padding: "3px 8px",
                            fontSize: 11,
                            cursor: "pointer",
                            borderRadius: 4,
                            border: "1px solid",
                            borderColor: isSelected ? "#22c55e" : "#94a3b8",
                            background: isSelected ? "#dcfce7" : "#f1f5f9",
                            color: isSelected ? "#16a34a" : "#64748b",
                        }}
                    >
                        Edge {i + 1}: {isSelected ? "ON" : "OFF"}
                    </button>
                );
            })}

            <Handle type="source" position={Position.Right} />
        </div>
    );
}
