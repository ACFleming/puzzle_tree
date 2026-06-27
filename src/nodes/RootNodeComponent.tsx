import { useGraphStore } from "../graphStore";
import type { NodeData } from "../types";
import BaseNode from "./BaseNode";

export default function RootNodeComponent({ data }: { data: NodeData }) {
    const toggleRoot = useGraphStore((s) => s.toggleRoot);

    return (
        <BaseNode
            data={{ ...data, label: "Root" }}
            hasInput={false}
            onClick={() => toggleRoot(data.modelId)}
        />
    );
}
