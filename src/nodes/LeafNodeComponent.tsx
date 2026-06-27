import type { NodeData } from "../types";
import BaseNode from "./BaseNode";

export default function LeafNodeComponent({ data }: { data: NodeData }) {
    return <BaseNode data={{ ...data, label: "Leaf" }} hasOutput={false} />;
}
