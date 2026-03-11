import React, { useRef, useEffect, useState } from 'react';
import styles from './styles.module.css';

const API_URL = 'http://localhost:8000/query';

/**
 * ChatWidget — floating book Q&A chatbot embedded on every Docusaurus page.
 *
 * Sends user questions to the FastAPI backend (POST /query) and renders
 * the grounded answer with clickable source citations.
 *
 * Injected globally via book/src/theme/Root.js (Docusaurus Root swizzle).
 */
export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (isOpen && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const query = inputValue.trim();

    // Empty input validation (FR-005 frontend guard)
    if (!query) {
      setMessages((prev) => [
        ...prev,
        { role: 'validation', text: 'Please enter a question before submitting.' },
      ]);
      return;
    }

    // Append user message
    setMessages((prev) => [...prev, { role: 'user', text: query }]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Server returned an error response (4xx / 5xx)
        const errorMsg = data.error || data.detail || 'An error occurred. Please try again.';
        setMessages((prev) => [...prev, { role: 'error', text: errorMsg }]);
        return;
      }

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: data.answer,
          sources: data.sources || [],
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'error', text: 'Failed to get a response. Please try again.' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      handleSubmit(e);
    }
  };

  return (
    <div className={styles.chatContainer}>
      {/* Toggle button */}
      <button
        className={styles.toggleButton}
        onClick={() => setIsOpen((prev) => !prev)}
        aria-label={isOpen ? 'Close chat' : 'Open book Q&A chat'}
        title="Ask the book"
      >
        {isOpen ? '✕' : '💬'}
      </button>

      {/* Chat panel */}
      {isOpen && (
        <div className={styles.chatPanel}>
          <div className={styles.panelHeader}>📖 Ask the Book</div>

          <div className={styles.messages}>
            {messages.length === 0 && (
              <div className={`${styles.message} ${styles.messageAssistant}`}>
                Hi! Ask me anything about this book and I&apos;ll answer using the book&apos;s content.
              </div>
            )}

            {messages.map((msg, i) => (
              <div key={i}>
                <div
                  className={`${styles.message} ${
                    msg.role === 'user'
                      ? styles.messageUser
                      : msg.role === 'error'
                      ? styles.messageError
                      : msg.role === 'validation'
                      ? styles.messageValidation
                      : styles.messageAssistant
                  }`}
                >
                  {msg.text}
                </div>

                {/* Source citations (T013) */}
                {msg.role === 'assistant' &&
                  msg.sources &&
                  msg.sources.length > 0 && (
                    <div className={styles.sources}>
                      <div className={styles.sourcesLabel}>Sources:</div>
                      {msg.sources.map((src, j) => (
                        <a
                          key={j}
                          href={src.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          title={src.url}
                        >
                          📄 {src.title || src.url}
                        </a>
                      ))}
                    </div>
                  )}
              </div>
            ))}

            {isLoading && (
              <div className={styles.loading}>⏳ Searching the book…</div>
            )}

            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className={styles.inputRow}>
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about the book…"
              disabled={isLoading}
              aria-label="Your question"
              autoComplete="off"
            />
            <button
              type="submit"
              className={styles.sendBtn}
              disabled={isLoading}
            >
              {isLoading ? '…' : 'Ask'}
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
