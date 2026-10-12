import { ArrowRight } from "lucide-react";
import "./SectionHeader.css";

export default function SectionHeader({
  title,
  subtitle,
  actionLabel,
  onAction,
}) {
  return (
    <div className="section-header">
      <div className="section-header__content">
        <h2 className="section-header__title">{title}</h2>

        {subtitle && (
          <p className="section-header__subtitle">{subtitle}</p>
        )}
      </div>

      {actionLabel && onAction && (
        <button
          type="button"
          className="section-header__action"
          onClick={onAction}
        >
          {actionLabel}
          <ArrowRight size={15} />
        </button>
      )}
    </div>
  );
}