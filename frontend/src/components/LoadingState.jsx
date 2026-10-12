import { LoaderCircle, Sparkles } from "lucide-react";
import "./LoadingState.css";

export default function LoadingState({
  title = "Working on your research",
  message = "Please wait while the AI processes your request.",
}) {
  return (
    <div className="loading-state" role="status" aria-live="polite">
      <div className="loading-state-visual">
        <span className="loading-state-orbit loading-orbit-one" />
        <span className="loading-state-orbit loading-orbit-two" />

        <div className="loading-state-icon">
          <Sparkles size={30} />
        </div>

        <LoaderCircle className="loading-state-spinner" size={19} />
      </div>

      <h3>{title}</h3>
      <p>{message}</p>

      <div className="loading-state-progress">
        <span />
      </div>
    </div>
  );
}