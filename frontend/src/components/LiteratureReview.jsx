import { useState } from "react";
import {
  AlertCircle, BookOpen, CheckCircle2, Copy, FileText,
  LoaderCircle, Sparkles, WandSparkles,
} from "lucide-react";
import api from "../services/api";
import "./LiteratureReview.css";

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  return error?.message || "Unable to generate the literature review. Please try again.";
}

function ReviewSection({ title, children }) {
  if (children == null || children === "" || (Array.isArray(children) && !children.length)) return null;
  return (
    <section className="literature-review-section">
      <h3>{title}</h3>
      {Array.isArray(children)
        ? <ul>{children.map((item, index) => <li key={index}>{String(item)}</li>)}</ul>
        : <p>{String(children)}</p>}
    </section>
  );
}

export default function LiteratureReview({ papers = [] }) {
  const [topic, setTopic] = useState("");
  const [selectedPaperIds, setSelectedPaperIds] = useState([]);
  const [review, setReview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  const handlePaperToggle = (paperId) => {
    setSelectedPaperIds((previous) =>
      previous.includes(paperId)
        ? previous.filter((id) => id !== paperId)
        : previous.length >= 10
          ? previous
          : [...previous, paperId],
    );
  };

  const handleGenerate = async (event) => {
    event.preventDefault();
    if (!topic.trim()) return setError("Enter a research topic first.");
    if (selectedPaperIds.length < 2) return setError("Select at least two research papers.");
    if (selectedPaperIds.length > 10) return setError("Select no more than ten papers.");

    setLoading(true);
    setError("");
    setReview(null);
    setCopied(false);
    try {
      const response = await api.post("/literature-review/", {
        research_topic: topic.trim(),
        paper_ids: selectedPaperIds,
      });
      setReview(response.data?.review ?? response.data?.result ?? response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const reviewAsText = () => {
    if (!review) return "";
    if (typeof review === "string") return review;
    const fields = [
      ["title", review.title],
      ["Research topic", review.research_topic],
      ["Introduction", review.introduction],
      ["Thematic analysis", review.thematic_analysis],
      ["Agreements and disagreements", review.agreements_and_disagreements],
      ["Research gaps", review.research_gaps],
      ["Conclusion", review.conclusion],
      ["References", review.references],
    ];
    return fields
      .filter(([, value]) => value != null && value !== "")
      .map(([label, value]) => `${label}\n${Array.isArray(value) ? value.map((item) => `• ${item}`).join("\n") : value}`)
      .join("\n\n");
  };

  const copyReview = async () => {
    try {
      await navigator.clipboard.writeText(reviewAsText());
      setCopied(true);
      setError("");
    } catch {
      setError("Could not copy automatically. You can select and copy the report text.");
    }
  };

  return (
    <main className="literature-review">
      <header className="literature-heading">
        <span className="literature-eyebrow"><Sparkles size={15} /> AI-POWERED SYNTHESIS</span>
        <h1>Literature Review</h1>
        <p>Synthesize research across selected papers to explore common themes, compare findings, and identify research gaps.</p>
      </header>

      <form className="literature-form soft-panel" onSubmit={handleGenerate}>
        <div className="literature-form-heading">
          <span className="literature-icon"><BookOpen size={24} /></span>
          <div><h2>Configure Your Review</h2><p>Choose a topic and select 2–10 indexed papers.</p></div>
        </div>

        <label className="literature-label" htmlFor="literature-topic">Research topic</label>
        <input
          id="literature-topic"
          className="literature-topic-input"
          type="text"
          value={topic}
          onChange={(event) => setTopic(event.target.value)}
          placeholder="e.g. Facial Emotion Recognition using Deep Learning"
          required
          disabled={loading}
        />

        <div className="literature-paper-heading">
          <div><h3>Select research papers</h3><p>{selectedPaperIds.length} selected · minimum 2, maximum 10</p></div>
          <FileText size={20} />
        </div>

        {papers.length ? (
          <div className="literature-paper-list">
            {papers.map((paper, index) => {
              const id = String(paper.paper_id || paper.id || "");
              const title = paper.title || paper.filename || paper.file_name || `Research Paper ${index + 1}`;
              const selected = selectedPaperIds.includes(id);
              return (
                <label className={`literature-paper-option ${selected ? "selected" : ""}`} key={id || index}>
                  <input
                    type="checkbox"
                    checked={selected}
                    disabled={loading || !id || (!selected && selectedPaperIds.length >= 10)}
                    onChange={() => handlePaperToggle(id)}
                  />
                  <span className="literature-paper-file"><FileText size={19} /></span>
                  <span className="literature-paper-title">{title}</span>
                  {selected && <CheckCircle2 size={18} className="literature-selected-icon" />}
                </label>
              );
            })}
          </div>
        ) : (
          <div className="literature-empty"><FileText size={25} /><p>No papers in this browser session. Upload your PDFs first.</p></div>
        )}

        {error && <div className="literature-error" role="alert"><AlertCircle size={18} /><span>{error}</span></div>}

        <button className="literature-generate-button" type="submit" disabled={loading || papers.length < 2}>
          {loading ? <><LoaderCircle size={18} className="literature-spin" /> Generating review...</> : <><WandSparkles size={18} /> Generate Literature Review</>}
        </button>
      </form>

      {loading && <div className="literature-loading" role="status"><LoaderCircle size={23} className="literature-spin" /><span>Reviewing selected papers. This may take a moment.</span></div>}

      {review && (
        <section className="literature-results soft-panel">
          <div className="literature-results-heading">
            <div><span className="literature-eyebrow">GENERATED REPORT</span><h2>{review.title || topic}</h2></div>
            <button type="button" className="literature-copy-button" onClick={copyReview}><Copy size={15} /> {copied ? "Copied" : "Copy Review"}</button>
          </div>
          {typeof review === "string" ? (
            <div className="literature-review-content">{review}</div>
          ) : (
            <div className="literature-review-content">
              <p><strong>Research topic:</strong> {review.research_topic || topic}</p>
              <ReviewSection title="Introduction">{review.introduction}</ReviewSection>
              <ReviewSection title="Thematic analysis">{review.thematic_analysis}</ReviewSection>
              <ReviewSection title="Agreements and disagreements">{review.agreements_and_disagreements}</ReviewSection>
              <ReviewSection title="Research gaps">{review.research_gaps}</ReviewSection>
              <ReviewSection title="Conclusion">{review.conclusion}</ReviewSection>
              <ReviewSection title="References">{review.references}</ReviewSection>
            </div>
          )}
        </section>
      )}
    </main>
  );
}
