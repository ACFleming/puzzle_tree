import type { NodeData } from "../types";
import BaseNode from "./BaseNode";

export default function ORNodeComponent({ data }: { data: NodeData }) {
    return <BaseNode data={{ ...data, label: "OR" }} />;
}
