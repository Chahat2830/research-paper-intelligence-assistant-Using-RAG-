
import { useRef, useState } from "react";
import {
  CheckCircle2,
  CloudUpload,
  FileText,
  LoaderCircle,
  X,
} from "lucide-react";

import "./PaperUpload.css";
import { uploadPaper } from "../services/papers";

export default function PaperUpload({ onUploadSuccess }) {
  const inputRef = useRef(null);

  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const selectFile = (selectedFile) => {
    setError("");
    setResult(null);
    setProgress(0);

    if (!selectedFile) return;

    if (
      selectedFile.type !== "application/pdf" &&
      !selectedFile.name.toLowerCase().endsWith(".pdf")
    ) {
      setFile(null);
      setError("Please select a PDF file.");
      return;
    }

    if (selectedFile.size > 20 * 1024 * 1024) {
      setFile(null);
      setError("PDF size must be 20 MB or less.");
      return;
    }

    if (selectedFile.size === 0) {
      setFile(null);
      setError("The selected PDF file is empty.");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setDragging(false);

    if (uploading) return;

    selectFile(event.dataTransfer.files?.[0]);
  };

  const handleUpload = async () => {
    if (!file || uploading) return;

    setUploading(true);
    setError("");
    setResult(null);
    setProgress(0);

    try {
      const data = await uploadPaper(file, setProgress);

      setResult(data);
      setProgress(100);

      if (typeof onUploadSuccess === "function") {
        onUploadSuccess(data);
      }
    } catch (err) {
      setError(
        err.message || "Failed to upload the paper. Please try again."
      );
    } finally {
      setUploading(false);
    }
  };

  const reset = () => {
    if (uploading) return;

    setFile(null);
    setResult(null);
    setError("");
    setProgress(0);

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  return (
    <div className="paper-upload">
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,application/pdf"
        hidden
        disabled={uploading}
        onChange={(event) => {
          selectFile(event.target.files?.[0]);
          event.target.value = "";
        }}
      />

      <div
        className={`paper-upload-zone ${dragging ? "dragging" : ""}`}
        role="button"
        tabIndex={uploading ? -1 : 0}
        aria-label="Select or drop a research paper PDF"
        aria-disabled={uploading}
        onClick={() => !uploading && inputRef.current?.click()}
        onKeyDown={(event) => {
          if (
            !uploading &&
            (event.key === "Enter" || event.key === " ")
          ) {
            event.preventDefault();
            inputRef.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          if (!uploading) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
      >
        <CloudUpload size={38} strokeWidth={1.6} />

        <h3>Upload Research Paper</h3>

        <p>Drag and drop your PDF here, or click to browse</p>

        <span>PDF files only · Maximum 20 MB</span>
      </div>

      {file && (
        <div className="paper-upload-file">
          <FileText size={22} />

          <div className="paper-upload-file-info">
            <strong>{file.name}</strong>
            <small>
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </small>
          </div>

          {!uploading && (
            <button
              type="button"
              onClick={reset}
              aria-label="Remove selected file"
            >
              <X size={18} />
            </button>
          )}
        </div>
      )}

      {uploading && (
        <div className="paper-upload-progress">
          <div className="paper-upload-progress-label">
            <span>Uploading and processing paper...</span>
            <span>{progress}%</span>
          </div>

          <div className="paper-upload-progress-track">
            <div style={{ width: `${progress}%` }} />
          </div>

          <small>
            {progress >= 100
              ? "Upload transferred. Waiting for server processing..."
              : "Transferring PDF to the server..."}
          </small>
        </div>
      )}

      {error && (
        <p className="paper-upload-error" role="alert">
          {error}
        </p>
      )}

      {result && (
        <div className="paper-upload-success" role="status">
          <CheckCircle2 size={20} />

          <div>
            <strong>Paper uploaded successfully!</strong>

            {result.filename && <p>{result.filename}</p>}

            {result.paper_id && <p>Paper ID: {result.paper_id}</p>}

            {result.message && <p>{result.message}</p>}
          </div>
        </div>
      )}

      {file && !result && (
        <button
          className="paper-upload-submit"
          type="button"
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading ? (
            <>
              <LoaderCircle size={18} className="spin" />
              Processing...
            </>
          ) : (
            <>
              <CloudUpload size={18} />
              Upload &amp; Process Paper
            </>
          )}
        </button>
      )}
    </div>
  );
}
