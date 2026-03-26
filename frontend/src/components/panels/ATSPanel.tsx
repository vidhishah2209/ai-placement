import { motion } from "framer-motion";
import { ATSScore } from "@/types";

const ICONS: Record<string, string> = {
  formatting: "📐", keywords: "🔑", action_verbs: "💪",
  quantified_metrics: "📈", section_completeness: "📋", overall_coherence: "🎯",
};

const scoreColor = (score: number, max: number) => {
  const pct = (score / max) * 100;
  if (pct >= 70) return "hsl(var(--success))";
  if (pct >= 40) return "hsl(var(--warning))";
  return "hsl(var(--destructive))";
};

const ATSPanel = ({ data }: { data: ATSScore }) => {
  const pct = data.total_score;
  const circumference = 2 * Math.PI * 60;
  const offset = circumference - (pct / 100) * circumference;
  const ringColor = pct >= 70 ? "hsl(var(--success))" : pct >= 40 ? "hsl(var(--warning))" : "hsl(var(--destructive))";

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">ATS Score</h1>
      <p className="text-sm text-muted-foreground mb-6">How your resume performs against Applicant Tracking Systems.</p>

      <div className="glass-card rounded-2xl p-8">
        {/* Score ring */}
        <div className="flex flex-col items-center mb-8">
          <motion.svg width={160} height={160} className="-rotate-90" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <circle cx={80} cy={80} r={60} fill="none" stroke="hsl(var(--border))" strokeWidth={10} />
            <motion.circle
              cx={80} cy={80} r={60} fill="none" stroke={ringColor} strokeWidth={10}
              strokeLinecap="round"
              strokeDasharray={circumference}
              initial={{ strokeDashoffset: circumference }}
              animate={{ strokeDashoffset: offset }}
              transition={{ duration: 1.2, ease: "easeOut" }}
            />
          </motion.svg>
          <div className="absolute mt-10 text-center">
            <span className="text-4xl font-extrabold text-foreground">{pct}</span>
            <span className="block text-xs text-muted-foreground mt-0.5">/ 100</span>
          </div>
        </div>

        {data.reasoning && (
          <p className="text-sm text-muted-foreground text-center mb-8 max-w-lg mx-auto">{data.reasoning}</p>
        )}

        {/* Breakdown grid */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-8">
          {Object.entries(data.breakdown || {}).map(([key, item]) => (
            <div key={key} className="rounded-xl bg-secondary/50 border border-border p-4">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">{ICONS[key] || "📊"}</span>
                <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">
                  {key.replace(/_/g, " ")}
                </span>
              </div>
              <div className="flex items-baseline gap-1 mb-2">
                <span className="text-lg font-bold text-foreground">{item.score}</span>
                <span className="text-xs text-muted-foreground">/ {item.max}</span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-muted overflow-hidden">
                <motion.div
                  className="h-full rounded-full"
                  style={{ backgroundColor: scoreColor(item.score, item.max) }}
                  initial={{ width: 0 }}
                  animate={{ width: `${(item.score / item.max) * 100}%` }}
                  transition={{ duration: 1, delay: 0.3 }}
                />
              </div>
              {item.feedback && <p className="text-[11px] text-muted-foreground mt-2 leading-relaxed">{item.feedback}</p>}
            </div>
          ))}
        </div>

        {/* Strengths / Weaknesses */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { title: "Strengths", items: data.strengths, color: "success", icon: "✅" },
            { title: "Weaknesses", items: data.weaknesses, color: "destructive", icon: "⚠️" },
          ].map((section) => (
            <div key={section.title} className="rounded-xl bg-secondary/30 border border-border p-5">
              <h3 className="text-sm font-bold text-foreground mb-3">{section.title}</h3>
              <ul className="space-y-2">
                {(section.items || []).map((item, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                    <span className="text-xs mt-0.5">{section.icon}</span>
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ATSPanel;
