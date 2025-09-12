import React from "react";

interface DeepAgentToggleProps {
  deepAgentEnabled: boolean;
  toggleDeepAgent: () => void;
}

export function DeepAgentToggle({
  deepAgentEnabled,
  toggleDeepAgent,
}: DeepAgentToggleProps) {
  return (
    <button
      className={`ml-auto py-1.5
        rounded-lg
        group
        inline-flex 
        items-center
        px-2
        transition-all
        duration-300
        ease-in-out
        ${
          deepAgentEnabled
            ? "bg-purple-highlight text-purple-text dark:bg-transparent"
            : "text-input-text hover:text-neutral-900 hover:bg-background-chat-hover dark:hover:text-neutral-50"
        }
      `}
      onClick={toggleDeepAgent}
      role="switch"
      aria-checked={deepAgentEnabled}
      title="Enable Deep Agent for enhanced query processing with planning, sub-agents, and memory management"
    >
      <svg
        width="16"
        height="16"
        viewBox="0 0 16 16"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <path
          d="M8 2C8 1.44772 7.55228 1 7 1C6.44772 1 6 1.44772 6 2V3.5C6 3.77614 5.77614 4 5.5 4H4C3.44772 4 3 4.44772 3 5V6.5C3 6.77614 3.22386 7 3.5 7H5C5.55228 7 6 7.44772 6 8C6 8.55228 5.55228 9 5 9H3.5C3.22386 9 3 9.22386 3 9.5V11C3 11.5523 3.44772 12 4 12H5.5C5.77614 12 6 12.2239 6 12.5V14C6 14.5523 6.44772 15 7 15C7.55228 15 8 14.5523 8 14V12.5C8 12.2239 8.22386 12 8.5 12H10C10.5523 12 11 11.5523 11 11V9.5C11 9.22386 10.7761 9 10.5 9H9C8.44772 9 8 8.55228 8 8C8 7.44772 8.44772 7 9 7H10.5C10.7761 7 11 6.77614 11 6.5V5C11 4.44772 10.5523 4 10 4H8.5C8.22386 4 8 3.77614 8 3.5V2Z"
          stroke="currentColor"
          strokeOpacity="0.8"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle
          cx="8"
          cy="8"
          r="1.5"
          stroke="currentColor"
          strokeOpacity="0.8"
          strokeWidth="1.5"
        />
      </svg>
      <span
        className={`text-sm font-medium overflow-hidden transition-all duration-300 ease-in-out ${
          deepAgentEnabled
            ? "max-w-[100px] opacity-100 ml-2"
            : "max-w-0 opacity-0 ml-0"
        }`}
        style={{
          display: "inline-block",
          whiteSpace: "nowrap",
        }}
      >
        Deep Agent
      </span>
    </button>
  );
}
