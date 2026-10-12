import "./ProgressBar.css";

export default function ProgressBar({
  value = 0,
  label,
  showPercentage = true,
  color = "blue",
  size = "medium",
}) {
  const progress = Math.min(100, Math.max(0, Number(value) || 0));

  return (
    <div className={`progress-bar progress-bar--${size}`}>
      {(label || showPercentage) && (
        <div className="progress-bar__header">
          {label && (
            <span className="progress-bar__label">{label}</span>
          )}

          {showPercentage && (
            <span className="progress-bar__percentage">
              {Math.round(progress)}%
            </span>
          )}
        </div>
      )}

      <div
        className="progress-bar__track"
        role="progressbar"
        aria-label={label || "Progress"}
        aria-valuemin={0}
        aria-valuemax={100}
        aria-valuenow={Math.round(progress)}
      >
        <div
          className={`progress-bar__fill progress-bar__fill--${color}`}
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );
}