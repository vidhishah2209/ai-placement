import { SkillGaps } from "@/types";
import { AlertTriangle, BookOpen, Layers } from "lucide-react";

const SkillGapPanel = ({ data }: { data: SkillGaps }) => {
  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Skill Gap Analysis</h1>
      <p className="text-sm text-muted-foreground mb-6">Critical gaps and frameworks to close them.</p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* LEFT: Critical Skills + Roadmap */}
        <div className="space-y-6">
          {/* Critical Missing */}
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-destructive mb-4 flex items-center gap-2">
              <AlertTriangle className="w-3.5 h-3.5" />
              Critical Missing Skills
            </h3>
            <div className="flex flex-wrap gap-2 mb-0">
              {(data.missing_critical || []).map((s) => (
                <span key={s} className="px-3 py-1.5 rounded-full text-xs font-semibold bg-destructive/10 text-destructive border border-destructive/20">
                  {s}
                </span>
              ))}
              {(!data.missing_critical || data.missing_critical.length === 0) && (
                <span className="text-sm text-muted-foreground">None — great job!</span>
              )}
            </div>
          </div>

          {/* Roadmap / Priority Actions */}
          {data.priority_actions && data.priority_actions.length > 0 && (
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-xs font-bold uppercase tracking-wider text-warning mb-4 flex items-center gap-2">
                <BookOpen className="w-3.5 h-3.5" />
                Action Roadmap
              </h3>
              <div className="relative">
                {/* Vertical timeline line */}
                <div className="absolute left-[11px] top-2 bottom-2 w-px bg-border" />

                <div className="space-y-4">
                  {data.priority_actions.map((a, i) => (
                    <div key={i} className="relative pl-8">
                      {/* Timeline dot */}
                      <div className={`absolute left-0 top-1.5 w-[23px] h-[23px] rounded-full border-2 flex items-center justify-center text-[9px] font-bold ${
                        a.priority === "high"
                          ? "border-destructive bg-destructive/15 text-destructive"
                          : a.priority === "medium"
                          ? "border-warning bg-warning/15 text-warning"
                          : "border-info bg-info/15 text-info"
                      }`}>
                        {i + 1}
                      </div>
                      <div className="rounded-xl bg-secondary/30 border border-border p-4">
                        <div className="flex items-center gap-2 mb-1">
                          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold uppercase ${
                            a.priority === "high" ? "bg-destructive/15 text-destructive" :
                            a.priority === "medium" ? "bg-warning/15 text-warning" :
                            "bg-info/15 text-info"
                          }`}>
                            {a.priority}
                          </span>
                          <span className="text-sm font-semibold text-foreground">{a.skill}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">{a.reason}</p>
                        {a.resource_hint && (
                          <p className="text-xs text-primary mt-1.5">💡 {a.resource_hint}</p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* RIGHT: Frameworks to Learn */}
        <div className="space-y-6">
          <div className="glass-card rounded-2xl p-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary mb-4 flex items-center gap-2">
              <Layers className="w-3.5 h-3.5" />
              Frameworks & Tools to Learn
            </h3>

            {data.frameworks_to_learn && data.frameworks_to_learn.length > 0 ? (
              <div className="space-y-3">
                {data.frameworks_to_learn.map((fw, i) => (
                  <div key={i} className="rounded-xl bg-secondary/30 border border-border p-4 hover:border-primary/30 transition-all">
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm font-semibold text-foreground">{fw.name}</span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase bg-primary/10 text-primary border border-primary/20">
                        {fw.category}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground">{fw.reason}</p>
                  </div>
                ))}
              </div>
            ) : (
              /* Fallback: show missing_recommended as frameworks */
              <div className="space-y-3">
                {(data.missing_recommended || []).map((s) => (
                  <div key={s} className="rounded-xl bg-secondary/30 border border-border p-4">
                    <span className="text-sm font-semibold text-foreground">{s}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recommended skills if frameworks also present */}
          {data.frameworks_to_learn && data.frameworks_to_learn.length > 0 && data.missing_recommended && data.missing_recommended.length > 0 && (
            <div className="glass-card rounded-2xl p-6">
              <h3 className="text-xs font-bold uppercase tracking-wider text-accent mb-4 flex items-center gap-2">
                ⚡ Also Recommended
              </h3>
              <div className="flex flex-wrap gap-2">
                {data.missing_recommended.map((s) => (
                  <span key={s} className="px-3 py-1.5 rounded-full text-xs font-semibold bg-accent/10 text-accent border border-accent/20">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SkillGapPanel;
