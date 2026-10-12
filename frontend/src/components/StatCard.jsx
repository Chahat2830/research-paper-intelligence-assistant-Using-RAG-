import {
  FileText,
  Brain,
  Layers3,
  TrendingUp,
} from "lucide-react";

import "./StatCard.css";

const iconMap = {
  papers: FileText,
  analyses: Brain,
  topics: Layers3,
  activity: TrendingUp,
};

export default function StatCard({
  title = "Total Papers",
  value = 0,
  change,
  description,
  icon = "papers",
  color = "blue",
}) {
  const Icon = iconMap[icon] || FileText;

  return (
    <article className={`stat-card stat-card--${color}`}>
      <div className="stat-card__top">
        <div className="stat-card__icon">
          <Icon size={21} strokeWidth={1.8} />
        </div>

        {change && (
          <span className="stat-card__change">
            <TrendingUp size={13} />
            {change}
          </span>
        )}
      </div>

      <div className="stat-card__content">
        <p className="stat-card__title">{title}</p>
        <h3 className="stat-card__value">{value}</h3>

        {description && (
          <p className="stat-card__description">
            {description}
          </p>
        )}
      </div>
    </article>
  );
}