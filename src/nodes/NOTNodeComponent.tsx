import type { NodeData } from "../types";
import BaseNode from "./BaseNode";

export default function NOTNodeComponent({ data }: { data: NodeData }) {
    return <BaseNode data={{ ...data, label: "NOT" }} />;
}
