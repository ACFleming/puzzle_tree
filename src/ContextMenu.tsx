// ContextMenu.tsx
import { useEffect, useRef } from "react";
import { createPortal} from "react-dom"

type MenuItem = {
    label: string;
    onSelect: () => void;
};

type Props = {
    x: number;
    y: number;
    items: MenuItem[];
    onClose: () => void;
};

export default function ContextMenu({ x, y, items, onClose }: Props) {
    const menuRef = useRef<HTMLDivElement>(null);

    // Close the menu if the user clicks anywhere outside it,
    // or presses Escape.
    useEffect(() => {
        function handleClickOutside(e: MouseEvent) {
            if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
                onClose();
            }
        }
        function handleEscape(e: KeyboardEvent) {
            if (e.key === "Escape") onClose();
        }

        document.addEventListener("mousedown", handleClickOutside, { capture: true });
        document.addEventListener("keydown", handleEscape);

        // Cleanup: remove listeners when this component unmounts
        // (i.e. when the menu closes). Skipping this is a common
        // source of "why is my handler firing twice" bugs.
        return () => {
            document.removeEventListener("mousedown", handleClickOutside, { capture: true });
            document.removeEventListener("keydown", handleEscape);
        };
    }, [onClose]);

    return createPortal(
        <div
            ref={menuRef}
            style={{
                position: "fixed",
                top: y,
                left: x,
                background: "#ffffff",
                border: "1px solid #cbd5e1",
                borderRadius: 6,
                boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
                minWidth: 140,
                zIndex: 1000,
                padding: 4,
            }}
        >
            {items.map((item) => (
                <div
                    key={item.label}
                    onClick={() => {
                        item.onSelect();
                        onClose();
                    }}
                    style={{
                        padding: "6px 12px",
                        fontSize: 13,
                        borderRadius: 4,
                        cursor: "pointer",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.background = "#f1f5f9")}
                    onMouseLeave={(e) => (e.currentTarget.style.background = "transparent")}
                >
                    {item.label}
                </div>
            ))}
        </div>,
        document.body
    );
}