import axios from "axios";
import api from "./api";

function getErrorMessage(error) {
  const detail = error.response?.data?.detail ?? error.response?.data?.message;

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (typeof item === "string") return item;

        const location = Array.isArray(item.loc)
          ? `${item.loc.join(" → ")}: `
          : "";

        return `${location}${item.msg || JSON.stringify(item)}`;
      })
      .join("; ");
  }

  if (detail && typeof detail === "object") {
    return JSON.stringify(detail);
  }

  return error.message || "An unexpected API error occurred.";
}

/**
 * Upload a PDF and index its text on the backend.
 */
export const uploadPaper = async (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  try {
    // Use axios directly here so FastAPI's original error response
    // remains available when an upload fails.
    const response = await axios.post(
      `${api.defaults.baseURL}/papers/upload`,
      formData,
      {
        timeout: 120000,
        onUploadProgress: (event) => {
          if (event.total && onUploadProgress) {
            onUploadProgress(Math.round((event.loaded * 100) / event.total));
          }
        },
      },
    );

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Analyze paper text.
 * Backend requires both paper_id and paper_text.
 */
export const analyzePaper = async (
  paperText,
  paperId = `frontend-${Date.now()}`,
) => {
  try {
    const response = await api.post("/analysis/", {
      paper_id: paperId,
      paper_text: paperText,
    });

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};

/**
 * Ask a question using the backend's chat schema.
 */
export const askPaperQuestion = async (paperId, question) => {
  try {
    const response = await api.post("/chat/", {
      question,
      paper_ids: paperId ? [paperId] : [],
      chat_history: [],
    });

    return response.data;
  } catch (error) {
    throw new Error(getErrorMessage(error));
  }
};
