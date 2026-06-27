import type { NodeData } from "../types";
import BaseNode from "./BaseNode";

export default function ANDNodeComponent({ data }: { data: NodeData }) {
    return <BaseNode data={{ ...data, label: "AND" }} />;
}
