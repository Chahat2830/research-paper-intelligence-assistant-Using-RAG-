import { useState } from "react";
import {
  AlertCircle, ArrowLeftRight, CheckCircle2, FileText,
  GitCompareArrows, LoaderCircle, Sparkles,
} from "lucide-react";
import api from "../services/api";
import "./ComparePapers.css";

const ASPECTS = [
  ["research_objectives", "Research objectives"],
  ["methodology", "Methodology"],
  ["datasets", "Datasets"],
  ["key_findings", "Key findings"],
  ["limitations", "Limitations"],
];

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map((item) => item.msg || JSON.stringify(item)).join("; ");
  return error?.message || "Comparison failed. Check the backend logs and try again.";
}

function displayValue(value) {
  if (value == null || value === "") return "Not provided in the selected paper text.";
  if (Array.isArray(value)) {
    return value.length ? value.map((item) => typeof item === "string" ? item : JSON.stringify(item)).join("\n• ") : "Not provided";
  }
  if (typeof value === "object") return JSON.stringify(value, null, 2);
  return String(value);
}

export default function ComparePapers({ papers = [], onComparisonSuccess }) {
  const [selectedIds, setSelectedIds] = useState(["", ""]);
  const [aspects, setAspects] = useState(ASPECTS.map(([value]) => value));
  const [comparison, setComparison] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const getPaperId = (paper) => String(paper.paper_id || paper.id || "");
  const getTitle = (paper, index) =>
    paper.title || paper.filename || paper.file_name || `Research Paper ${index + 1}`;

  const handleCompare = async (event) => {
    event.preventDefault();
    const ids = selectedIds.map((id) => id.trim()).filter(Boolean);
    if (ids.length !== 2) {
      setError("Select two research papers to compare.");
      return;
    }
    if (ids[0] === ids[1]) {
      setError("Choose two different papers.");
      return;
    }

    setLoading(true);
    setError("");
    setComparison(null);
    try {
      const response = await api.post("/comparison/", {
        paper_ids: ids,
        comparison_aspects: aspects,
      });
      setComparison(response.data);
      onComparisonSuccess?.(response.data);
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  const toggleAspect = (aspect) => {
    setAspects((current) =>
      current.includes(aspect)
        ? current.filter((item) => item !== aspect)
        : [...current, aspect],
    );
  };

  const result = comparison?.comparison ?? comparison?.result ?? comparison;
  const resultPapers = Array.isArray(result?.papers) ? result.papers : [];
  const summaryKeys = [
    ["overall_summary", "Overall summary"],
    ["common_themes", "Common themes"],
    ["key_differences", "Key differences"],
    ["research_gaps", "Research gaps"],
  ];

  return (
    <main className="compare-papers">
      <header className="compare-heading">
        <span className="compare-eyebrow"><Sparkles size={15} /> RESEARCH SIDE BY SIDE</span>
        <h1>Compare Papers</h1>
        <p>Compare research objectives, methods, datasets, findings, and limitations across your indexed papers.</p>
      </header>

      <form className="compare-selector-panel" onSubmit={handleCompare}>
        <div className="compare-selector-heading">
          <GitCompareArrows size={22} />
          <h2>Select research papers</h2>
        </div>

        {papers.length < 2 && (
          <p className="compare-helper">Upload and index at least two papers before comparing them.</p>
        )}

        <div className="compare-selectors">
          {[0, 1].map((slot) => (
            <label key={slot}>
              <span><FileText size={16} /> {slot === 0 ? "First paper" : "Second paper"}</span>
              <select
                value={selectedIds[slot]}
                onChange={(event) => {
                  const next = [...selectedIds];
                  next[slot] = event.target.value;
                  setSelectedIds(next);
                }}
                required
                disabled={loading}
              >
                <option value="">Choose a paper</option>
                {papers.map((paper, index) => {
                  const id = getPaperId(paper);
                  return (
                    <option key={id || index} value={id} disabled={!id || (selectedIds[1 - slot] === id)}>
                      {getTitle(paper, index)}
                    </option>
                  );
                })}
              </select>
            </label>
          ))}
          <span className="compare-versus"><ArrowLeftRight size={21} /> VS</span>
        </div>

        <fieldset className="compare-aspects">
          <legend>What should be compared?</legend>
          <div className="compare-aspect-options">
            {ASPECTS.map(([value, label]) => (
              <label key={value}>
                <input type="checkbox" checked={aspects.includes(value)} onChange={() => toggleAspect(value)} disabled={loading} />
                <span>{label}</span>
              </label>
            ))}
          </div>
        </fieldset>

        {error && <div className="compare-error" role="alert"><AlertCircle size={19} /><span>{error}</span></div>}

        <button className="compare-submit" type="submit" disabled={loading || papers.length < 2 || aspects.length === 0}>
          {loading ? <><LoaderCircle size={18} className="compare-spin" /> Comparing papers...</> : <><GitCompareArrows size={18} /> Compare Papers</>}
        </button>
      </form>

      {comparison && (
        <section className="compare-results" aria-live="polite">
          <div className="compare-results-heading">
            <div><span className="compare-eyebrow">COMPARISON REPORT</span><h2>Research Comparison</h2></div>
            <span className="compare-complete"><CheckCircle2 size={16} /> Complete</span>
          </div>

          <div className="compare-paper-names">
            {selectedIds.map((id, index) => {
              const paper = papers.find((item) => getPaperId(item) === id);
              return <article key={id}><span>Paper {index === 0 ? "A" : "B"}</span><h3>{paper ? getTitle(paper, papers.indexOf(paper)) : id}</h3></article>;
            })}
          </div>

          {summaryKeys.map(([key, label]) => {
            const value = result?.[key];
            if (value == null || value === "" || (Array.isArray(value) && !value.length)) return null;
            return <article className="compare-result-card" key={key}><h3>{label}</h3><p>{displayValue(value)}</p></article>;
          })}

          {resultPapers.length > 0 && (
            <div className="compare-result-list">
              {resultPapers.map((paper, index) => (
                <article className="compare-result-card" key={paper.paper_id || index}>
                  <h3>{paper.title || papers.find((item) => getPaperId(item) === paper.paper_id)?.title || `Paper ${index + 1}`}</h3>
                  {[
                    ["research_objectives", "Research objectives"],
                    ["methodology", "Methodology"],
                    ["datasets", "Datasets"],
                    ["key_findings", "Key findings"],
                    ["strengths", "Strengths"],
                    ["limitations", "Limitations"],
                  ].map(([key, label]) => (
                    <p key={key}><strong>{label}:</strong> {displayValue(paper[key])}</p>
                  ))}
                </article>
              ))}
            </div>
          )}

          {!resultPapers.length && !summaryKeys.some(([key]) => result?.[key] != null) && (
            <pre className="compare-raw-result">{JSON.stringify(result, null, 2)}</pre>
          )}
        </section>
      )}
    </main>
  );
}
