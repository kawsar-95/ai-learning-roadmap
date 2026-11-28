import type { WalkNodeKind } from "@/lib/content-schema";

/** A 20 × 20 line icon for each kind of box. */
export function Icon({ kind }: { kind: WalkNodeKind }) {
  const line = {
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.7,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
  };
  switch (kind) {
    case "user":
      return (
        <g {...line}>
          <circle cx="10" cy="6.5" r="3.5" />
          <path d="M3.5 18c0-3.9 2.9-6.2 6.5-6.2s6.5 2.3 6.5 6.2" />
        </g>
      );
    case "browser":
      return (
        <g {...line}>
          <rect x="2" y="3.5" width="16" height="13" rx="2" />
          <path d="M2 7.5h16M4.8 5.5h.01M7 5.5h.01" />
        </g>
      );
    case "dns":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M2.5 10h15M10 2.5c2.2 2.1 3.2 4.6 3.2 7.5s-1 5.4-3.2 7.5c-2.2-2.1-3.2-4.6-3.2-7.5s1-5.4 3.2-7.5z" />
        </g>
      );
    case "server":
      return (
        <g {...line}>
          <rect x="3" y="3" width="14" height="6" rx="1.5" />
          <rect x="3" y="11" width="14" height="6" rx="1.5" />
          <path d="M6 6h.01M6 14h.01" />
        </g>
      );
    case "database":
      return (
        <g {...line}>
          <ellipse cx="10" cy="4.8" rx="6.5" ry="2.3" />
          <path d="M3.5 4.8v10.4c0 1.3 2.9 2.3 6.5 2.3s6.5-1 6.5-2.3V4.8M3.5 10c0 1.3 2.9 2.3 6.5 2.3s6.5-1 6.5-2.3" />
        </g>
      );
    case "cache":
      return (
        <g {...line}>
          <path d="M11 2.5 4.5 11h5l-1 6.5L15.5 9h-5z" />
        </g>
      );
    case "cdn":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M2.5 10h15M10 2.5v15" />
          <circle cx="10" cy="10" r="2.2" />
        </g>
      );
    case "balancer":
      return (
        <g {...line}>
          <path d="M2.5 10h5l4-5h5M7.5 10l4 5h5M14.5 3l2.5 2-2.5 2M14.5 13l2.5 2-2.5 2" />
        </g>
      );
    case "queue":
      return (
        <g {...line}>
          <rect x="2.5" y="6" width="4" height="8" rx="1" />
          <rect x="8" y="6" width="4" height="8" rx="1" />
          <rect x="13.5" y="6" width="4" height="8" rx="1" />
        </g>
      );
    case "storage":
      return (
        <g {...line}>
          <rect x="2.5" y="4" width="15" height="4" rx="1" />
          <path d="M3.5 8v7.5h13V8M8 11h4" />
        </g>
      );
    case "service":
      return (
        <g {...line}>
          <rect x="3" y="3" width="14" height="14" rx="3.5" />
          <circle cx="10" cy="10" r="3" />
        </g>
      );
    case "lock":
      return (
        <g {...line}>
          <rect x="4.5" y="9" width="11" height="8" rx="2" />
          <path d="M6.8 9V6.6a3.2 3.2 0 0 1 6.4 0V9M10 12.2v2" />
        </g>
      );
    case "key":
      return (
        <g {...line}>
          <circle cx="6.5" cy="13.5" r="3.5" />
          <path d="M9 11 17 3M14 6l2.5 2.5M11.8 8.2l2 2" />
        </g>
      );
    case "shield":
      return (
        <g {...line}>
          <path d="M10 2.5 4 5v4.6c0 4 2.6 6.8 6 7.9 3.4-1.1 6-3.9 6-7.9V5z" />
          <path d="m7.3 10 2.1 2.1 3.5-3.9" />
        </g>
      );
    case "clock":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="7.5" />
          <path d="M10 5.5V10l3 2" />
        </g>
      );
    case "chart":
      return (
        <g {...line}>
          <path d="M3 3v14h14" />
          <path d="m6 13 3-4 3 2 4-6" />
        </g>
      );
    case "file":
      return (
        <g {...line}>
          <path d="M5 2.5h6.5L15 6v11.5H5z" />
          <path d="M11.5 2.5V6H15M7.5 10h5M7.5 13h5" />
        </g>
      );
    case "model":
      return (
        <g {...line}>
          <circle cx="10" cy="10" r="2.4" />
          <circle cx="3.8" cy="4.5" r="1.8" />
          <circle cx="16.2" cy="4.5" r="1.8" />
          <circle cx="3.8" cy="15.5" r="1.8" />
          <circle cx="16.2" cy="15.5" r="1.8" />
          <path d="M5.3 5.6l3 2.7M14.7 5.6l-3 2.7M5.3 14.4l3-2.7M14.7 14.4l-3-2.7" />
        </g>
      );
    case "tool":
      return (
        <g {...line}>
          <path d="M7.6 3.2c-1.8 0-2.6.9-2.6 2.6v1.7c0 1.1-.7 2-1.9 2.5 1.2.5 1.9 1.4 1.9 2.5v1.7c0 1.7.8 2.6 2.6 2.6M12.4 3.2c1.8 0 2.6.9 2.6 2.6v1.7c0 1.1.7 2 1.9 2.5-1.2.5-1.9 1.4-1.9 2.5v1.7c0 1.7-.8 2.6-2.6 2.6" />
        </g>
      );
    case "note":
      return null;
  }
}
