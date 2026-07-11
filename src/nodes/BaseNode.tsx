import { useState } from "react";
import { Handle, Position} from "@xyflow/react";
import type { NodeData } from "../types";
import ContextMenu from "../ContextMenu";
import { useGraphStore } from "../graphStore";

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
    // null = menu closed. Otherwise, holds the screen coords to render it at.
    const [menuPos, setMenuPos] = useState<{ x: number; y: number } | null>(null);
    const removeNode = useGraphStore((s) => s.removeNode);
    return (
        <div
            onClick={onClick}
            onContextMenu={(e) =>{
                    e.preventDefault()
                    setMenuPos({ x: e.clientX, y: e.clientY });
                } 
            }
            style={{
                padding: "8px 16px",
                borderRadius: 8,
                border: "2px solid",
                borderColor: menuPos ? "#007afd" : 
                    data.state ? "#22c55e" : "#94a3b8",
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

            {menuPos && (
                <ContextMenu
                    x={menuPos.x}
                    y={menuPos.y}
                    onClose={() => setMenuPos(null)}
                    items={[
                        { label: "Toggle state", onSelect: () => console.log("toggle") },
                        { label: "Delete node", onSelect: () => console.log("TODO: Implement Delete") },
                    ]}
                />
            )}
        </div>
    );
}
