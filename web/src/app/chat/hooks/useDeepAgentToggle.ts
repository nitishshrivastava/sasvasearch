import { useState, useEffect, useRef, useCallback } from "react";

interface UseDeepAgentToggleProps {
  chatSessionId: string | null;
  assistantId: number | undefined;
}

/**
 * Custom hook for managing the deep agent toggle state.
 * Automatically resets the toggle to false when:
 * - Switching between existing chat sessions
 * - The assistant changes
 * - The page is reloaded (since state initializes to false)
 *
 * The toggle is preserved when transitioning from no chat session to a new session.
 *
 * @param chatSessionId - The current chat session ID
 * @param assistantId - The current assistant ID
 * @returns An object containing the toggle state and toggle function
 */
export function useDeepAgentToggle({
  chatSessionId,
  assistantId,
}: UseDeepAgentToggleProps) {
  const [deepAgentEnabled, setDeepAgentEnabled] = useState(false);
  const previousChatSessionId = useRef<string | null>(chatSessionId);

  // Reset when switching chat sessions, but preserve when going from null to a new session
  useEffect(() => {
    const previousId = previousChatSessionId.current;
    previousChatSessionId.current = chatSessionId;

    // Only reset if we're switching between actual sessions (not from null to a new session)
    if (previousId !== null && previousId !== chatSessionId) {
      setDeepAgentEnabled(false);
    }
  }, [chatSessionId]);

  // Reset when switching assistants
  useEffect(() => {
    setDeepAgentEnabled(false);
  }, [assistantId]);

  const toggleDeepAgent = useCallback(() => {
    setDeepAgentEnabled(!deepAgentEnabled);
  }, [deepAgentEnabled]);

  return {
    deepAgentEnabled,
    toggleDeepAgent,
  };
}
