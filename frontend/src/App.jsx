import { useState } from "react";
import {
  Activity,
  ArrowRight,
  BarChart3,
  BookOpen,
  Bot,
  ChevronDown,
  FileText,
  Flame,
  Layers3,
  MessageSquare,
  Search,
  Bell,
  Upload,
  UserRound,
  Home,
  GitCompareArrows,
  CloudUpload,
  Zap,
  MoreVertical,
  Sparkles,
} from "lucide-react";

import "./App.css";
import PaperUpload from "./components/PaperUpload";
import ResearchChat from "./components/ResearchChat";
import PaperAnalysis from "./components/PaperAnalysis";
import FeedbackState from "./components/FeedbackState";
import ComparePapers from "./components/ComparePapers";
import LiteratureReview from "./components/LiteratureReview";

const navigationItems = [
  { label: "Dashboard", icon: Home },
  { label: "My Papers", icon: FileText },
  { label: "Research Chat", icon: MessageSquare },
  { label: "Paper Analysis", icon: BarChart3 },
  { label: "Compare Papers", icon: Layers3 },
  { label: "Literature Review", icon: BookOpen },
];

const researchTools = [
  {
    title: "Research Chat",
    description: "Ask questions and get answers with source references.",
    icon: MessageSquare,
    color: "blue",
    page: "Research Chat",
  },
  {
    title: "Paper Analysis",
    description: "Get detailed analysis, key findings, methodology and more.",
    icon: BarChart3,
    color: "orange",
    page: "Paper Analysis",
  },
  {
    title: "Compare Papers",
    description: "Compare multiple papers side by side.",
    icon: Layers3,
    color: "green",
    page: "Compare Papers",
  },
  {
    title: "Literature Review",
    description: "Generate comprehensive literature reviews on any topic.",
    icon: BookOpen,
    color: "purple",
    page: "Literature Review",
  },
];

const initialPapers = [];

const topics = [
  "Computer Vision",
  "Deep Learning",
  "Neural Networks",
  "NLP",
  "Transformers",
  "Recommender Systems",
];

const quickActions = [
  {
    title: "Upload PDF",
    icon: CloudUpload,
    color: "blue",
    page: "My Papers",
  },
  {
    title: "Start Chat",
    icon: MessageSquare,
    color: "green",
    page: "Research Chat",
  },
  {
    title: "Analyze Paper",
    icon: BarChart3,
    color: "purple",
    page: "Paper Analysis",
  },
  {
    title: "Compare Papers",
    icon: Layers3,
    color: "orange",
    page: "Compare Papers",
  },
];

function Sidebar({ activePage, onNavigate }) {
  return (
    <aside className="sidebar">
      <button
        className="brand"
        onClick={() => onNavigate("Dashboard")}
        aria-label="Go to dashboard"
      >
        <span className="brand-icon">
          <Layers3 size={23} />
        </span>

        <span className="brand-copy">
          <strong>Research Paper</strong>
          <span>Intelligence Assistant</span>
        </span>
      </button>

      <nav className="sidebar-nav" aria-label="Main navigation">
        {navigationItems.map(({ label, icon: Icon }) => (
          <button
            key={label}
            className={`nav-item ${
              activePage === label ? "active" : ""
            }`}
            onClick={() => onNavigate(label)}
          >
            <Icon size={20} strokeWidth={1.8} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-quote">
        <span className="quote-mark">“</span>

        <p>
          Turn complex research papers into clear insights with AI.
        </p>

        <div className="sidebar-art-placeholder">
          <Sparkles size={34} strokeWidth={1.3} />
          <span>DISCOVER · ANALYZE · LEARN</span>
        </div>
      </div>

      <button className="profile-button">
        <span className="profile-avatar">
          <UserRound size={24} />
        </span>

        <span className="profile-copy">
          <strong>Chahat</strong>
          <span>Research Explorer</span>
        </span>
      </button>
    </aside>
  );
}

function Topbar({ searchQuery, setSearchQuery }) {
  return (
    <header className="topbar">
      <div className="topbar-context">
        <span>EXPLORE</span>
        <span>×</span>
        <span>ANALYZE</span>
        <span>×</span>
        <span>COMPARE</span>
        <span>×</span>
        <span>DISCOVER</span>
      </div>

      <div className="topbar-actions">
        <label className="search-box">
          <Search size={18} />

          <input
            type="search"
            placeholder="Search papers, topics..."
            value={searchQuery}
            onChange={(event) => setSearchQuery(event.target.value)}
            aria-label="Search papers and topics"
          />
        </label>

        <button className="icon-button" aria-label="Notifications">
          <Bell size={20} />
          <span className="notification-dot" />
        </button>

        <button className="topbar-avatar" aria-label="User profile">
          C
        </button>
      </div>
    </header>
  );
}

function Hero({ onNavigate }) {
  return (
    <section className="hero">
      <div className="hero-content">
        <div className="eyebrow">
          <Sparkles size={14} />
          YOUR PERSONAL RESEARCH WORKSPACE
        </div>

        <h1>
          Your AI <span>Research</span> Assistant
        </h1>

        <p>
          Upload research papers, ask questions, analyze, compare
          and generate literature reviews — all in one place.
        </p>

        <div className="hero-actions">
          <button
            className="primary-button"
            onClick={() => onNavigate("My Papers")}
          >
            <Upload size={17} />
            Upload Paper
            <ArrowRight size={17} />
          </button>

          <button
            className="secondary-button"
            onClick={() => onNavigate("Research Chat")}
          >
            <MessageSquare size={17} />
            Start Chat
            <ArrowRight size={17} />
          </button>
        </div>
      </div>

      <div className="hero-visual" aria-label="AI research assistant artwork">
        <div className="visual-orbit orbit-one" />
        <div className="visual-orbit orbit-two" />

        <div className="floating-symbol symbol-one">
          <Bot size={27} />
        </div>

        <div className="floating-symbol symbol-two">
          <BarChart3 size={27} />
        </div>

        <div className="robot-illustration">
          <Bot size={116} strokeWidth={1.1} />
          <span>AI</span>
        </div>

        <div className="floating-document document-one">
          <FileText size={34} />
          <span />
          <span />
          <span />
        </div>

        <div className="floating-document document-two">
          <Activity size={28} />
          <span />
          <span />
        </div>
      </div>
    </section>
  );
}

function QuickStats({ papers, analysesDone = 0, comparisonsDone = 0 }) {
  const stats = [
    {
      label: "Papers Uploaded",
      value: papers.length,
      icon: FileText,
      color: "blue",
    },
    {
      label: "Total Chunks",
      value: papers.reduce((sum, paper) => sum + paper.chunks, 0),
      icon: Layers3,
      color: "green",
    },
    {
      label: "Analyses Done",
      value: analysesDone,
      icon: BarChart3,
      color: "purple",
    },
    {
      label: "Comparisons",
      value: comparisonsDone,
      icon: GitCompareArrows,
      color: "orange",
    },
  ];

  return (
    <section className="stats-panel soft-panel">
      <div className="panel-heading">
        <Sparkles size={18} />
        <h2>Quick Stats</h2>
      </div>

      <div className="stats-grid">
        {stats.map(({ label, value, icon: Icon, color }) => (
          <div className="stat-card" key={label}>
            <span className={`stat-icon ${color}`}>
              <Icon size={21} />
            </span>

            <div>
              <strong>{value}</strong>
              <span>{label}</span>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeatureCards({ onNavigate }) {
  return (
    <section className="feature-grid" aria-label="Research tools">
      {researchTools.map(
        ({ title, description, icon: Icon, color, page }) => (
          <button
            className="feature-card soft-panel"
            key={title}
            onClick={() => onNavigate(page)}
          >
            <span className={`feature-icon ${color}`}>
              <Icon size={24} />
            </span>

            <span className="feature-copy">
              <strong>{title}</strong>
              <span>{description}</span>
            </span>

            <ArrowRight className="feature-arrow" size={18} />
          </button>
        ),
      )}
    </section>
  );
}

function RecentPapers({ papers, searchQuery, onNavigate }) {
  const filteredPapers = papers.filter((paper) =>
    paper.title.toLowerCase().includes(searchQuery.toLowerCase()),
  );

  return (
    <section className="papers-panel soft-panel">
      <div className="section-heading">
        <div className="heading-title">
          <FileText size={20} />
          <h2>Recent Papers</h2>
        </div>

        <button
          className="text-button"
          onClick={() => onNavigate("My Papers")}
        >
          View All <ArrowRight size={15} />
        </button>
      </div>

      {filteredPapers.length > 0 ? (
        <div className="paper-grid">
          {filteredPapers.map((paper) => (
            <article className="paper-card" key={paper.id}>
              <button
                className="paper-menu"
                aria-label={`More options for ${paper.title}`}
              >
                <MoreVertical size={17} />
              </button>

              <div className={`paper-preview ${paper.color}`}>
                <div className="preview-page">
                  <span className="preview-title" />
                  {Array.from({ length: 5 }, (_, index) => (
                    <span className="preview-line" key={index} />
                  ))}
                </div>

                <div className="preview-page preview-page-back">
                  <span className="preview-title" />
                  {Array.from({ length: 4 }, (_, index) => (
                    <span className="preview-line" key={index} />
                  ))}
                </div>

                <span className="pdf-badge">PDF</span>
              </div>

              <h3 title={paper.title}>{paper.title}</h3>
              <p>{paper.date}</p>
              <span className="paper-chunks">
                {paper.chunks} chunks
              </span>
            </article>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          <Search size={24} />
          <p>No papers match “{searchQuery}”.</p>
        </div>
      )}
    </section>
  );
}

function ActivityOverview() {
  const points = "10,116 52,91 94,103 136,63 178,80 220,42 262,58";
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

  return (
    <section className="activity-panel soft-panel">
      <div className="section-heading">
        <div className="heading-title">
          <Activity size={20} />
          <h2>Activity Overview</h2>
        </div>

        <button className="period-button">
          This Week <ChevronDown size={14} />
        </button>
      </div>

      <div className="chart-area">
        <div className="chart-y-labels">
          <span>40</span>
          <span>30</span>
          <span>20</span>
          <span>10</span>
          <span>0</span>
        </div>

        <div className="chart-main">
          <svg
            className="activity-chart"
            viewBox="0 0 272 145"
            preserveAspectRatio="none"
            role="img"
            aria-label="Illustrative weekly research activity chart"
          >
            <defs>
              <linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#477aff" stopOpacity=".28" />
                <stop offset="100%" stopColor="#477aff" stopOpacity=".02" />
              </linearGradient>
              <linearGradient id="chartLine" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor="#258cff" />
                <stop offset="100%" stopColor="#8759ff" />
              </linearGradient>
            </defs>

            {[20, 48, 76, 104, 132].map((y) => (
              <line
                key={y}
                x1="0"
                y1={y}
                x2="272"
                y2={y}
                stroke="#cbd8ec"
                strokeWidth=".8"
              />
            ))}

            <polygon
              points={`10,132 ${points} 262,132`}
              fill="url(#chartFill)"
            />

            <polyline
              points={points}
              fill="none"
              stroke="url(#chartLine)"
              strokeWidth="3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            <circle cx="220" cy="42" r="5" fill="#6c5cff" stroke="white" strokeWidth="2" />
          </svg>

          <div className="chart-x-labels">
            {labels.map((label) => (
              <span key={label}>{label}</span>
            ))}
          </div>
        </div>
      </div>

      <p className="chart-note">
        <span className="chart-note-dot" />
        Illustrative activity overview
      </p>
    </section>
  );
}

function PopularTopics({ onTopicSelect }) {
  return (
    <section className="topics-panel soft-panel">
      <div className="section-heading">
        <div className="heading-title">
          <Flame size={20} className="flame-icon" />
          <h2>Popular Topics</h2>
        </div>
      </div>

      <div className="topic-list">
        {topics.map((topic) => (
          <button
            key={topic}
            className="topic-chip"
            onClick={() => onTopicSelect(topic)}
          >
            {topic}
          </button>
        ))}
      </div>
    </section>
  );
}

function QuickActions({ onNavigate }) {
  return (
    <section className="quick-actions-panel soft-panel">
      <div className="section-heading">
        <div className="heading-title">
          <Zap size={20} className="zap-icon" />
          <h2>Quick Actions</h2>
        </div>
      </div>

      <div className="quick-actions-grid">
        {quickActions.map(
          ({ title, icon: Icon, color, page }) => (
            <button
              key={title}
              className="quick-action"
              onClick={() => onNavigate(page)}
            >
              <span className={`quick-action-icon ${color}`}>
                <Icon size={22} />
              </span>

              <span>{title}</span>
            </button>
          ),
        )}
      </div>
    </section>
  );
}

function Dashboard({
  onNavigate,
  searchQuery,
  papers,
  onTopicSelect,
  analysesDone,
  comparisonsDone,
}) {
  return (
    <>
      <div className="dashboard-top-grid">
        <Hero onNavigate={onNavigate} />
        <QuickStats papers={papers} analysesDone={analysesDone} comparisonsDone={comparisonsDone} />
      </div>

      <FeatureCards onNavigate={onNavigate} />

      <div className="content-grid">
        <RecentPapers
          papers={papers}
          searchQuery={searchQuery}
          onNavigate={onNavigate}
        />

        <ActivityOverview />
      </div>

      <div className="bottom-grid">
        <PopularTopics onTopicSelect={onTopicSelect} />
        <QuickActions onNavigate={onNavigate} />
      </div>
    </>
  );
}

function App() {
  const [activePage, setActivePage] = useState("Dashboard");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedTopic, setSelectedTopic] = useState("");
  const [papers, setPapers] = useState(initialPapers);
  const [uploadedPaper, setUploadedPaper] = useState(null);
  const [analysesDone, setAnalysesDone] = useState(0);
  const [comparisonsDone, setComparisonsDone] = useState(0);

  const activePaperId = uploadedPaper?.paper_id || papers[0]?.id || "";

  function handleUploadSuccess(data) {
    setUploadedPaper(data);
    const paperId = data.paper_id || data.id || `uploaded-${Date.now()}`;
    const paperTitle =
      data.filename || data.file_name || data.title || "Uploaded research paper";

    const newPaper = {
      id: paperId,
      paper_id: paperId,
      title: paperTitle,
      filename: paperTitle,
      date: new Date().toLocaleDateString("en-IN", {
        month: "short",
        day: "2-digit",
        year: "numeric",
      }),
      chunks: Number(
        data.chunks_created ?? data.chunk_count ?? data.chunks ?? 0,
      ),
      color: "blue",
      status: data.status || "processed",
    };

    setPapers((current) => [
      newPaper,
      ...current.filter((paper) => String(paper.id) !== String(paperId)),
    ]);
  }

  function navigateTo(page) {
    setActivePage(page);
    setSelectedTopic("");
  }

  function selectTopic(topic) {
    setSelectedTopic(topic);
    setSearchQuery(topic);
    setActivePage("Dashboard");
  }

  return (
    <div className="app-shell">
      <Sidebar activePage={activePage} onNavigate={navigateTo} />

      <main className="main-content">
        <Topbar
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
        />

        {activePage === "Dashboard" ? (
          <Dashboard
            onNavigate={navigateTo}
            searchQuery={searchQuery}
            papers={papers}
            onTopicSelect={selectTopic}
            analysesDone={analysesDone}
            comparisonsDone={comparisonsDone}
          />
        ) : activePage === "My Papers" ? (
          <section className="papers-workspace">
            <div className="section-heading dashboard-upload-heading">
              <div>
                <p className="eyebrow">YOUR RESEARCH LIBRARY</p>
                <h1>My Papers</h1>
                <p>
                  Upload a PDF and prepare it for your research workflow.
                  Papers are shown for this browser session only.
                </p>
              </div>
            </div>

            <PaperUpload onUploadSuccess={handleUploadSuccess} />

            {uploadedPaper && (
              <p className="upload-result-message" role="status">
                Upload completed:{" "}
                {uploadedPaper.filename || uploadedPaper.file_name || "your paper"}.
                The paper is indexed by the backend and listed in this session.
              </p>
            )}

            <div className="papers-workspace-list">
              <RecentPapers
                papers={papers}
                searchQuery={searchQuery}
                onNavigate={navigateTo}
              />
            </div>
          </section>
        ) : activePage === "Research Chat" ? (
          activePaperId ? (
            <ResearchChat paperId={activePaperId} />
          ) : (
            <section className="papers-workspace">
              <FeedbackState
                type="empty"
                title="Upload a paper to start chatting"
                message="Upload a text-based PDF in My Papers first. The chat uses the indexed paper chunks in the backend."
                actionLabel="Go to My Papers"
                onAction={() => navigateTo("My Papers")}
              />
            </section>
          )
        ) : activePage === "Paper Analysis" ? (
          <PaperAnalysis />
        ) : activePage === "Compare Papers" ? (
          <section className="papers-workspace">
            <ComparePapers
              papers={papers}
              onComparisonSuccess={() => setComparisonsDone((count) => count + 1)}
            />
          </section>
        ) : activePage === "Literature Review" ? (
          <section className="papers-workspace">
            <LiteratureReview papers={papers} />
          </section>
        ) : (
          <section className="placeholder-page soft-panel">
            <span className="placeholder-icon">
              <Sparkles size={30} />
            </span>
            <p className="eyebrow">RESEARCH WORKSPACE</p>
            <h1>{activePage}</h1>
            <p className="placeholder-description">
              {selectedTopic
                ? `Explore research related to ${selectedTopic}.`
                : `Your ${activePage.toLowerCase()} workspace will appear here.`}
            </p>
            <button
              className="primary-button"
              onClick={() => navigateTo("Dashboard")}
            >
              <Home size={17} />
              Back to Dashboard
              <ArrowRight size={17} />
            </button>
          </section>
        )}

        <footer className="app-footer">
          <span>
            <Sparkles size={14} />
            Research Paper Intelligence Assistant
          </span>
          <span>Built for curious minds.</span>
        </footer>
      </main>
    </div>
  );
}
export default App;