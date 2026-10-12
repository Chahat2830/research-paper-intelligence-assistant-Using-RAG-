import { useState } from "react";
import {
  Activity,
  AlertCircle,
  BarChart3,
  BookOpen,
  CheckCircle2,
  FileText,
  FlaskConical,
  LoaderCircle,
  Sparkles,
  Target,
} from "lucide-react";

import { analyzePaper } from "../services/papers";
import "./PaperAnalysis.css";

const analysisSections = [
  {
    key: "summary",
    title: "Executive Summary",
    icon: BookOpen,
  },
  {
    key: "methodology",
    title: "Methodology",
    icon: FlaskConical,
  },
  {
    key: "key_findings",
    title: "Key Findings",
    icon: Target,
  },
  {
    key: "limitations",
    title: "Limitations",
    icon: Activity,
  },
  {
    key: "conclusion",
    title: "Conclusion",
    icon: CheckCircle2,
  },
];

function formatContent(value) {
  if (typeof value === "string") return value;

  if (Array.isArray(value)) {
    return value
      .map((item) =>
        typeof item === "string" ? item : JSON.stringify(item, null, 2),
      )
      .join("\n\n");
  }

  if (value && typeof value === "object") {
    return JSON.stringify(value, null, 2);
  }

  return "";
}

function getSections(result) {
  const data = result?.analysis ?? result?.result ?? result;

  if (typeof data === "string") {
    return [{ key: "summary", title: "Analysis Results", content: data }];
  }

  if (!data || typeof data !== "object" || Array.isArray(data)) {
    return [];
  }

  return analysisSections
    .map((section) => ({
      ...section,
      content: formatContent(data[section.key]),
    }))
    .filter((section) => section.content);
}

export default function PaperAnalysis() {
  const [paperText, setPaperText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const sections = result ? getSections(result) : [];

  const handleAnalyze = async (event) => {
    event.preventDefault();

    if (!paperText.trim() || loading) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const response = await analyzePaper(paperText.trim());
      setResult(response);
    } catch (err) {
      setError(err.message || "Unable to analyze the research paper.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="paper-analysis">
      <header className="analysis-heading">
        <span className="analysis-eyebrow">
          <Sparkles size={15} />
          AI-POWERED RESEARCH
        </span>

        <h1>Paper Analysis</h1>

        <p>
          Extract meaningful insights, understand research methodology,
          and review key findings from academic papers.
        </p>
      </header>

      <form className="analysis-input-panel" onSubmit={handleAnalyze}>
        <div className="analysis-panel-heading">
          <span className="analysis-icon">
            <FileText size={23} />
          </span>

          <div>
            <h2>Research Paper Content</h2>
            <p>Paste the text you want the AI to analyze.</p>
          </div>
        </div>

        <label className="analysis-text-label" htmlFor="paper-analysis-text">
          Paper text
        </label>

        <textarea
          id="paper-analysis-text"
          value={paperText}
          onChange={(event) => setPaperText(event.target.value)}
          placeholder="Paste the abstract, methodology, results, or full paper text here..."
          rows={10}
          required
          disabled={loading}
        />

        <div className="analysis-input-footer">
          <span>{paperText.length.toLocaleString()} characters</span>

          <button
            type="submit"
            className="analysis-submit-button"
            disabled={loading || !paperText.trim()}
          >
            {loading ? (
              <>
                <LoaderCircle size={18} className="analysis-spin" />
                Analyzing...
              </>
            ) : (
              <>
                <BarChart3 size={18} />
                Analyze Paper
              </>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="analysis-error" role="alert">
          <AlertCircle size={19} />
          <span>{error}</span>
        </div>
      )}

      {loading && (
        <div className="analysis-loading" role="status">
          <LoaderCircle size={24} className="analysis-spin" />
          <span>Analyzing the paper. This may take a moment.</span>
        </div>
      )}

      {result && (
        <section className="analysis-results" aria-live="polite">
          <div className="analysis-results-heading">
            <div>
              <span className="analysis-eyebrow">YOUR RESULTS</span>
              <h2>Analysis Report</h2>
            </div>

            <span className="analysis-complete">
              <CheckCircle2 size={16} />
              Completed
            </span>
          </div>

          {sections.length > 0 ? (
            <div className="analysis-results-grid">
              {sections.map((section) => {
                const Icon = section.icon || FileText;

                return (
                  <article
                    className="analysis-result-card"
                    key={section.key}
                  >
                    <div className="analysis-result-title">
                      <span>
                        <Icon size={19} />
                      </span>

                      <h3>{section.title}</h3>
                    </div>

                    <div className="analysis-result-content">
                      {section.content}
                    </div>
                  </article>
                );
              })}
            </div>
          ) : (
            <pre className="analysis-raw-result">
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </section>
      )}
    </main>
  );
}