import { Handle, Position } from "@xyflow/react";
import type { NodeData } from "../types";

type Props = {
    data: NodeData;
    hasInput?: boolean;
    hasOutput?: boolean;
    onClick?: () => void;
};

/**
 * Shared visual wrapper for all node types.
 * Renders the node box, label, state indicator, and connection handles.
 * hasInput/hasOutput control whether handles are shown.
 */
export default function BaseNode({
    data,
    hasInput = true,
    hasOutput = true,
    onClick,
}: Props) {
    return (
        <div
            onClick={onClick}
            style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "2px solid",
                borderColor: data.state ? "#22c55e" : "#94a3b8",
                background: data.state ? "#dcfce7" : "#f1f5f9",
                minWidth: 80,
                textAlign: "center",
                cursor: onClick ? "pointer" : "default",
                transition: "all 0.15s ease",
            }}
        >
            {hasInput && <Handle type="target" position={Position.Left} />}

            <div style={{ fontWeight: 600, fontSize: 13 }}>{data.label}</div>

            <div
                style={{
                    fontSize: 11,
                    color: data.state ? "#16a34a" : "#64748b",
                }}
            >
                {data.state ? "TRUE" : "FALSE"}
            </div>

            {hasOutput && <Handle type="source" position={Position.Right} />}
        </div>
    );
}
