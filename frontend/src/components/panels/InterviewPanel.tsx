import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";
import { InterviewQNA } from "@/types";

const difficultyClass = (d: string) => {
  const l = d.toLowerCase();
  if (l === "easy") return "bg-success/15 text-success";
  if (l === "medium") return "bg-warning/15 text-warning";
  return "bg-destructive/15 text-destructive";
};

const InterviewPanel = ({ data }: { data: InterviewQNA }) => {
  const [open, setOpen] = useState<Record<number, boolean>>({});
  const [activeTab, setActiveTab] = useState<"All" | "Technical" | "HR" | "Project">("All");

  const getTabForCategory = (cat: string) => {
    const l = cat.toLowerCase();
    if (l.includes("hr")) return "HR";
    if (l.includes("project")) return "Project";
    if (l.includes("technical") || l.includes("dsa") || l.includes("fundamentals") || l.includes("design")) return "Technical";
    return "Other";
  };

  const filteredQuestions = (data.questions || []).filter(q => {
    if (activeTab === "All") return true;
    return getTabForCategory(q.category) === activeTab;
  });

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Interview Preparation</h1>
      <p className="text-sm text-muted-foreground mb-6">Personalized questions based on your resume and target role.</p>

      <div className="glass-card rounded-2xl p-6 mb-6">
        {/* Meta & Tabs */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
          <div className="flex gap-3">
            <span className="px-3 py-1.5 rounded-lg bg-secondary text-xs font-semibold text-foreground">
              Total: {data.questions?.length || 0}
            </span>
            <span className="px-3 py-1.5 rounded-lg bg-secondary text-xs font-semibold text-foreground">
              Difficulty: {data.estimated_difficulty}
            </span>
          </div>

          <div className="flex items-center gap-2 p-1 bg-secondary/50 rounded-xl border border-border overflow-x-auto hide-scrollbar">
            {["All", "Technical", "HR", "Project"].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab as any)}
                className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap ${
                  activeTab === tab
                    ? "bg-background text-foreground shadow-sm border border-border"
                    : "text-muted-foreground hover:text-foreground hover:bg-background/50"
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Tips */}
        {data.interview_tips && data.interview_tips.length > 0 && (
          <div className="rounded-xl bg-primary/5 border border-primary/15 p-4 mb-6">
            <h4 className="text-xs font-bold text-primary mb-2">💡 Tips</h4>
            <ul className="space-y-1">
              {data.interview_tips.map((t, i) => (
                <li key={i} className="text-xs text-muted-foreground">• {t}</li>
              ))}
            </ul>
          </div>
        )}

        {/* Questions */}
        <div className="space-y-3">
          {filteredQuestions.length === 0 ? (
            <div className="text-center py-8 text-sm text-muted-foreground">No questions found for this category.</div>
          ) : (
            filteredQuestions.map((q, i) => (
              <div key={q.id} className="rounded-xl border border-border overflow-hidden">
                <button
                  onClick={() => setOpen((o) => ({ ...o, [q.id]: !o[q.id] }))}
                  className="w-full flex flex-col md:flex-row md:items-center gap-3 p-4 text-left hover:bg-secondary/30 transition-all"
                >
                  <div className="w-full flex items-center justify-between md:hidden">
                    <span className="w-6 h-6 rounded-full bg-primary/10 text-primary text-[10px] font-bold flex items-center justify-center">
                      {i + 1}
                    </span>
                    <div className="flex items-center gap-2">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary">{getTabForCategory(q.category)}</span>
                      <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${difficultyClass(q.difficulty)}`}>{q.difficulty}</span>
                      <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${open[q.id] ? "rotate-180" : ""}`} />
                    </div>
                  </div>
                  
                  <span className="hidden md:flex w-7 h-7 rounded-full bg-primary/10 text-primary text-xs font-bold items-center justify-center flex-shrink-0">
                    {i + 1}
                  </span>
                  
                  <span className="flex-1 text-sm font-medium text-foreground">{q.question}</span>
                  
                  <div className="hidden md:flex items-center gap-2 flex-shrink-0">
                    <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-primary/10 text-primary">{getTabForCategory(q.category)}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${difficultyClass(q.difficulty)}`}>{q.difficulty}</span>
                    <ChevronDown className={`w-4 h-4 text-muted-foreground transition-transform ${open[q.id] ? "rotate-180" : ""}`} />
                  </div>
                </button>

                <AnimatePresence>
                  {open[q.id] && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: "auto", opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      className="overflow-hidden"
                    >
                      <div className="px-4 pb-4 pt-0 md:pt-2 border-t border-border">
                        {q.context && (
                          <div className="mt-3 mb-3">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Context</span>
                            <p className="text-xs text-muted-foreground mt-1">{q.context}</p>
                          </div>
                        )}
                        <div className="mb-3">
                          <span className="text-[10px] font-bold uppercase tracking-wider text-primary">Model Answer</span>
                          <div className="mt-1 space-y-1.5 text-sm text-foreground/70">
                            {q.model_answer?.intro && <p>{q.model_answer.intro}</p>}
                            {q.model_answer?.core && <p>{q.model_answer.core}</p>}
                            {q.model_answer?.example && <p className="italic text-muted-foreground">📌 {q.model_answer.example}</p>}
                            {q.model_answer?.conclusion && <p className="font-semibold text-foreground/80">{q.model_answer.conclusion}</p>}
                          </div>
                        </div>
                        {q.follow_up && (
                          <div className="rounded-lg bg-secondary/50 p-3">
                            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Follow-up</span>
                            <p className="text-xs text-foreground/70 mt-1">{q.follow_up}</p>
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default InterviewPanel;
