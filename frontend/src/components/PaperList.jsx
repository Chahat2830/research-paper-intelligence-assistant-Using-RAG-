import { FileText, Layers3, CheckCircle2, Clock3 } from "lucide-react";

function formatDate(value) {
  if (!value) return "Date unavailable";

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return "Date unavailable";

  return date.toLocaleDateString("en-IN", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function PaperList({ papers = [] }) {
  if (papers.length === 0) {
    return (
      <section className="paper-list-empty">
        <span className="paper-list-empty-icon">
          <FileText size={28} />
        </span>

        <h3>No research papers yet</h3>
        <p>Upload a PDF to start building your research library.</p>
      </section>
    );
  }

  return (
    <section className="paper-list" aria-label="Uploaded research papers">
      {papers.map((paper, index) => {
        const title =
          paper.title ||
          paper.filename ||
          paper.file_name ||
          `Research Paper ${index + 1}`;

        const chunks = Number(paper.chunks ?? paper.chunk_count ?? 0);
        const status = paper.status || "Uploaded";
        const paperId = paper.paper_id || paper.id || index;

        return (
          <article className="paper-list-item" key={paperId}>
            <span className="paper-list-file-icon">
              <FileText size={23} />
            </span>

            <div className="paper-list-details">
              <h3 title={title}>{title}</h3>

              <div className="paper-list-meta">
                <span>
                  <Clock3 size={14} />
                  {formatDate(paper.uploaded_at || paper.date)}
                </span>

                <span>
                  <Layers3 size={14} />
                  {chunks} chunks
                </span>
              </div>
            </div>

            <span
              className={`paper-list-status ${
                status.toLowerCase() === "processed" ||
                status.toLowerCase() === "success"
                  ? "is-processed"
                  : ""
              }`}
            >
              <CheckCircle2 size={15} />
              {status}
            </span>
          </article>
        );
      })}
    </section>
  );
}