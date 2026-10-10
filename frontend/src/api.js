const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export async function fetchStatus() {
  const res = await fetch(`${API_BASE}/api/status`);
  return res.json();
}

export async function fetchSessions() {
  const res = await fetch(`${API_BASE}/api/sessions`);
  return res.json();
}

export async function fetchSession(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`);
  return res.json();
}

export async function deleteSession(sessionId) {
  const res = await fetch(`${API_BASE}/api/sessions/${sessionId}`, { method: 'DELETE' });
  return res.json();
}

export async function fetchNotes(query = '') {
  const url = query ? `${API_BASE}/api/notes?query=${encodeURIComponent(query)}` : `${API_BASE}/api/notes`;
  const res = await fetch(url);
  return res.json();
}

export async function saveNote(title, content, tags = '') {
  const res = await fetch(`${API_BASE}/api/notes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, content, tags }),
  });
  return res.json();
}

export async function deleteNote(noteId) {
  const res = await fetch(`${API_BASE}/api/notes/${noteId}`, { method: 'DELETE' });
  return res.json();
}

export async function fetchQuizzes() {
  const res = await fetch(`${API_BASE}/api/quizzes`);
  return res.json();
}

export async function saveQuizResult(topic, score, total, sessionId = null, details = {}) {
  const res = await fetch(`${API_BASE}/api/quizzes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, score, total, session_id: sessionId, details }),
  });
  return res.json();
}

export async function generateFlashcards(topic, content) {
  const res = await fetch(`${API_BASE}/api/study/flashcards`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, content }),
  });
  return res.json();
}

export async function generateQuiz(topic, content, n = 5) {
  const res = await fetch(`${API_BASE}/api/study/quiz`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ topic, content, n }),
  });
  return res.json();
}

export function streamAgentExecution(goal, sessionId, onEvent, onError, onComplete) {
  const url = `${API_BASE}/api/agent/stream`;
  
  fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ goal, session_id: sessionId }),
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop(); // keep last incomplete chunk

        for (const block of lines) {
          if (!block.trim()) continue;
          const blockLines = block.split('\n');
          let eventType = 'message';
          let eventData = '';

          for (const line of blockLines) {
            if (line.startsWith('event: ')) {
              eventType = line.slice(7).trim();
            } else if (line.startsWith('data: ')) {
              eventData = line.slice(6);
            }
          }

          if (eventData) {
            try {
              const parsed = JSON.parse(eventData);
              onEvent({ type: eventType, data: parsed });
            } catch (err) {
              console.error('Failed to parse SSE event data', err, eventData);
            }
          }
        }
      }
      if (onComplete) onComplete();
    })
    .catch((err) => {
      console.error('Stream error:', err);
      if (onError) onError(err);
    });
}
