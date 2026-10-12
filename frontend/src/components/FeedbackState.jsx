import {
  AlertCircle,
  CheckCircle2,
  FileSearch,
  Info,
  RefreshCw,
} from "lucide-react";

import "./FeedbackState.css";

const stateConfig = {
  empty: {
    icon: FileSearch,
    title: "Nothing here yet",
    color: "blue",
  },
  error: {
    icon: AlertCircle,
    title: "Something went wrong",
    color: "red",
  },
  success: {
    icon: CheckCircle2,
    title: "Completed successfully",
    color: "green",
  },
  info: {
    icon: Info,
    title: "Information",
    color: "blue",
  },
};

export default function FeedbackState({
  type = "empty",
  title,
  message = "",
  actionLabel,
  onAction,
}) {
  const config = stateConfig[type] || stateConfig.empty;
  const Icon = config.icon;

  return (
    <div className={`feedback-state feedback-state--${config.color}`}>
      <div className="feedback-state__icon">
        <Icon size={25} strokeWidth={1.8} />
      </div>

      <h3>{title || config.title}</h3>

      {message && (
        <p className="feedback-state__message">{message}</p>
      )}

      {actionLabel && onAction && (
        <button
          type="button"
          className="feedback-state__button"
          onClick={onAction}
        >
          {type === "error" && <RefreshCw size={15} />}
          {actionLabel}
        </button>
      )}
    </div>
  );
}