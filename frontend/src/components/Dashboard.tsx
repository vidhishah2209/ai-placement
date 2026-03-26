import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User, AnalysisResponse, SectionId } from "@/types";
import { BarChart3, Target, FileEdit, Mic, Rocket, LogOut, X } from "lucide-react";
import UploadPanel from "./panels/UploadPanel";
import ATSPanel from "./panels/ATSPanel";
import SkillGapPanel from "./panels/SkillGapPanel";
import ResumePanel from "./panels/ResumePanel";
import InterviewPanel from "./panels/InterviewPanel";
import ConfidencePanel from "./panels/ConfidencePanel";
import Chatbot from "./Chatbot";

interface DashboardProps {
  user: User;
  onLogout: () => void;
}

const RESULT_TABS: { id: SectionId; icon: typeof BarChart3; label: string }[] = [
  { id: "ats", icon: BarChart3, label: "ATS Score" },
  { id: "skills", icon: Target, label: "Skill Gaps" },
  { id: "resume", icon: FileEdit, label: "Improved Resume" },
  { id: "interview", icon: Mic, label: "Interview Prep" },
  { id: "confidence", icon: Rocket, label: "Confidence" },
];

const Dashboard = ({ user, onLogout }: DashboardProps) => {
  const [response, setResponse] = useState<AnalysisResponse | null>(null);
  const [openPanel, setOpenPanel] = useState<SectionId | null>(null);

  const hasResults = !!response;

  const renderOpenPanel = () => {
    if (!response || !openPanel) return null;
    switch (openPanel) {
      case "ats": return <ATSPanel data={response.ats_score} />;
      case "skills": return <SkillGapPanel data={response.skill_gaps} />;
      case "resume": return <ResumePanel data={response.improved_resume} supervisorPassed={response.supervisor_passed} />;
      case "interview": return <InterviewPanel data={response.interview_qna} />;
      case "confidence": return <ConfidencePanel data={response.confidence_score} />;
      default: return null;
    }
  };

  return (
    <div className="min-h-screen" style={{ background: "var(--gradient-hero)" }}>
      {/* Top bar */}
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
              <Rocket className="w-4 h-4 text-primary-foreground" />
            </div>
            <span className="text-sm font-bold text-foreground">AI Placement Cell</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-[10px] font-bold text-primary-foreground" style={{ background: "var(--gradient-primary)" }}>
                {user.name?.[0]?.toUpperCase() || "U"}
              </div>
              <span className="text-xs text-muted-foreground">{user.name}</span>
            </div>
            <button
              onClick={onLogout}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium text-destructive/70 hover:text-destructive hover:bg-destructive/10 transition-all"
            >
              <LogOut className="w-3.5 h-3.5" />
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-6 py-8">
        {/* Upload section - always visible */}
        <UploadPanel
          userId={user.user_id}
          onAnalysisComplete={(data) => { setResponse(data); }}
          onNavigate={() => {}}
        />

        {/* Result tabs - appear after analysis */}
        <AnimatePresence>
          {hasResults && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, ease: "easeOut" }}
              className="mt-8"
            >
              <p className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">Analysis Results</p>
              <div className="flex flex-wrap gap-3">
                {RESULT_TABS.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setOpenPanel(tab.id)}
                    className={`group flex items-center gap-2.5 px-5 py-3 rounded-xl text-sm font-semibold transition-all duration-200 glow-border ${
                      openPanel === tab.id
                        ? "text-primary-foreground shadow-lg"
                        : "glass-card text-foreground hover:border-primary/40"
                    }`}
                    style={openPanel === tab.id ? { background: "var(--gradient-primary)", boxShadow: "var(--shadow-glow)" } : undefined}
                  >
                    <tab.icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Panel content modal overlay */}
        <AnimatePresence>
          {openPanel && response && (
            <motion.div
              key={openPanel}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="fixed inset-0 z-50 flex items-start justify-center pt-12 pb-8 px-4 overflow-y-auto"
              style={{ background: "hsla(228, 30%, 5%, 0.85)", backdropFilter: "blur(8px)" }}
              onClick={(e) => { if (e.target === e.currentTarget) setOpenPanel(null); }}
            >
              <motion.div
                initial={{ opacity: 0, y: 30, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: 20, scale: 0.97 }}
                transition={{ duration: 0.3, ease: "easeOut" }}
                className="w-full max-w-5xl glass-card rounded-2xl p-8 relative"
              >
                <button
                  onClick={() => setOpenPanel(null)}
                  className="absolute top-4 right-4 w-9 h-9 rounded-xl flex items-center justify-center text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
                >
                  <X className="w-5 h-5" />
                </button>
                {renderOpenPanel()}
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Floating Placement Assistant */}
      <Chatbot />
    </div>
  );
};

export default Dashboard;
