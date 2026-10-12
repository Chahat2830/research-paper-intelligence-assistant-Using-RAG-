import { useState } from "react";
import {
  Bot,
  Send,
  UserRound,
  Sparkles,
  LoaderCircle,
  AlertCircle,
} from "lucide-react";

import { askPaperQuestion } from "../services/papers";
import "./ResearchChat.css";

export default function ResearchChat({ paperId }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (event) => {
    event.preventDefault();

    const trimmedQuestion = question.trim();

    if (!trimmedQuestion || loading) return;

    if (!paperId) {
      setError("Upload a research paper before starting a chat.");
      return;
    }

    setError("");
    setQuestion("");
    setMessages((previous) => [
      ...previous,
      { role: "user", content: trimmedQuestion },
    ]);
    setLoading(true);

    try {
      const response = await askPaperQuestion(paperId, trimmedQuestion);

      const answer =
        response.answer ||
        response.response ||
        response.message ||
        "The API returned no answer.";

      setMessages((previous) => [
        ...previous,
        { role: "assistant", content: answer },
      ]);
    } catch (err) {
      setError(err.message || "Unable to get an answer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="research-chat soft-panel">
      <header className="research-chat-header">
        <span className="research-chat-icon">
          <Bot size={24} />
        </span>

        <div>
          <h2>Research Chat</h2>
          <p>Ask questions about your research paper.</p>
        </div>

        <Sparkles size={20} className="research-chat-sparkle" />
      </header>

      <div className="research-chat-messages" aria-live="polite">
        {messages.length === 0 && (
          <div className="research-chat-welcome">
            <span>
              <Sparkles size={26} />
            </span>
            <h3>Let's explore your research</h3>
            <p>
              Ask about the methodology, key findings, limitations, or
              conclusions of your uploaded paper.
            </p>
          </div>
        )}

        {messages.map((message, index) => (
          <div
            className={`research-chat-message ${
              message.role === "user" ? "user-message" : "assistant-message"
            }`}
            key={`${message.role}-${index}`}
          >
            <span className="research-chat-message-avatar">
              {message.role === "user" ? (
                <UserRound size={18} />
              ) : (
                <Bot size={18} />
              )}
            </span>

            <div className="research-chat-bubble">
              <strong>
                {message.role === "user" ? "You" : "AI Assistant"}
              </strong>
              <p>{message.content}</p>
            </div>
          </div>
        ))}

        {loading && (
          <div className="research-chat-loading">
            <LoaderCircle size={18} className="research-chat-spin" />
            <span>Analyzing your question...</span>
          </div>
        )}
      </div>

      {error && (
        <p className="research-chat-error" role="alert">
          <AlertCircle size={16} />
          {error}
        </p>
      )}

      <form className="research-chat-form" onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          placeholder="Ask something about your paper..."
          aria-label="Your research question"
          disabled={loading}
        />

        <button
          type="submit"
          disabled={loading || !question.trim()}
          aria-label="Send question"
        >
          {loading ? (
            <LoaderCircle size={19} className="research-chat-spin" />
          ) : (
            <Send size={19} />
          )}
        </button>
      </form>

      <p className="research-chat-disclaimer">
        AI responses may contain errors. Verify important findings against
        the original paper.
      </p>
    </section>
  );
}