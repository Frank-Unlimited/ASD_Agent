/**
 * API Service for ASD Agent
 * Connects to local Python backend
 */

// Configuration
// Backend runs on 0.0.0.0:7860
export const API_BASE_URL = 'http://localhost:8000';

// Toggle this to false to force using Mock Data in the frontend (if implemented)
export const USE_REAL_API = true;

export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
}

export interface ToolCall {
    tool_name: string;
    tool_display_name: string;
    result: {
        success: boolean;
        message: string;
        data?: any;
    };
}

export interface ChatResponse {
    response: string;
    conversation_history: ChatMessage[];
    tool_calls: ToolCall[];
}

export interface StreamEvent {
    type: 'tool_call' | 'tool_result' | 'content' | 'done' | 'error';
    data: any;
}

// Session Management
const SESSION_KEY = 'asd_agent_session_id';

export const getSessionId = (): string => {
    let sessionId = localStorage.getItem(SESSION_KEY);
    if (!sessionId) {
        sessionId = crypto.randomUUID();
        localStorage.setItem(SESSION_KEY, sessionId);
    }
    return sessionId;
};

export const clearSession = () => {
    localStorage.removeItem(SESSION_KEY);
};

// API Methods
export const ApiService = {
    /**
     * Send a chat message (non-streaming)
     */
    async sendMessage(
        message: string,
        childId: string,
        history: ChatMessage[] = []
    ): Promise<ChatResponse> {
        const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                child_id: childId,
                conversation_history: history,
                // session_id: getSessionId() // Backend support pending
            }),
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        return await response.json();
    },

    /**
     * Send a chat message (streaming via SSE)
     */
    async streamMessage(
        message: string,
        childId: string,
        history: ChatMessage[],
        onEvent: (event: StreamEvent) => void
    ): Promise<void> {
        const response = await fetch(`${API_BASE_URL}/api/chat/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message,
                child_id: childId,
                conversation_history: history,
                // session_id: getSessionId() // Backend support pending
            }),
        });

        if (!response.ok) {
            throw new Error(`API Error: ${response.status} ${response.statusText}`);
        }

        if (!response.body) {
            throw new Error('ReadableStream not supported');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.trim()) continue;

                    const eventMatch = line.match(/^event: (.+)$/m);
                    const dataMatch = line.match(/^data: (.+)$/m);

                    if (eventMatch && dataMatch) {
                        const type = eventMatch[1] as StreamEvent['type'];
                        try {
                            const data = JSON.parse(dataMatch[1]);
                            onEvent({ type, data });
                        } catch (e) {
                            console.error('Failed to parse SSE data', e);
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    },

    // Health Check
    async checkHealth(): Promise<boolean> {
        try {
            const res = await fetch(`${API_BASE_URL}/api/chat/health`);
            return res.ok;
        } catch (e) {
            return false;
        }
    }
};
