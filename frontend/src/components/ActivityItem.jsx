import {
  FileUp,
  Brain,
  MessageSquare,
  GitCompareArrows,
  BookOpen,
  CheckCircle2,
  Clock3,
} from "lucide-react";

import "./ActivityItem.css";

const activityIcons = {
  upload: FileUp,
  analysis: Brain,
  chat: MessageSquare,
  comparison: GitCompareArrows,
  literature: BookOpen,
};

export default function ActivityItem({
  type = "upload",
  title,
  description,
  timestamp,
  status = "completed",
}) {
  const Icon = activityIcons[type] || FileUp;

  return (
    <div className="activity-item">
      <div className={`activity-item__icon activity-item__icon--${type}`}>
        <Icon size={18} strokeWidth={1.8} />
      </div>

      <div className="activity-item__content">
        <h4 className="activity-item__title">{title}</h4>

        {description && (
          <p className="activity-item__description">{description}</p>
        )}

        {timestamp && (
          <span className="activity-item__timestamp">
            <Clock3 size={12} />
            {timestamp}
          </span>
        )}
      </div>

      <div className={`activity-item__status activity-item__status--${status}`}>
        {status === "completed" && <CheckCircle2 size={13} />}

        {status === "completed"
          ? "Completed"
          : status === "pending"
            ? "Pending"
            : status === "failed"
              ? "Failed"
              : status}
      </div>
    </div>
  );
}