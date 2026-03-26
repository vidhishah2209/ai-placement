import { motion } from "framer-motion";
import { ConfidenceScore } from "@/types";

const TIER_ICONS: Record<string, { icon: string; label: string }> = {
  service_based: { icon: "🏢", label: "Service-Based" },
  mid_tier_product: { icon: "🏗️", label: "Mid-Tier Product" },
  top_product: { icon: "🌟", label: "Top Product" },
};

const ConfidencePanel = ({ data }: { data: ConfidenceScore }) => {
  const pct = data.confidence_percentage;
  const color = pct >= 70 ? "hsl(var(--success))" : pct >= 40 ? "hsl(var(--warning))" : "hsl(var(--destructive))";

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Placement Confidence</h1>
      <p className="text-sm text-muted-foreground mb-6">Overall readiness assessment for campus placements.</p>

      <div className="glass-card rounded-2xl p-8">
        {/* Confidence % */}
        <div className="text-center mb-6">
          <motion.span
            className="text-5xl font-extrabold"
            style={{ color }}
            initial={{ opacity: 0, scale: 0.5 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5, type: "spring" }}
          >
            {pct}%
          </motion.span>
          <p className="text-sm text-muted-foreground mt-1">Placement Confidence</p>
        </div>

        {data.summary && <p className="text-sm text-muted-foreground text-center mb-8 max-w-lg mx-auto">{data.summary}</p>}

        {/* Tier grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {Object.entries(data.tier_readiness || {}).map(([key, tier]) => {
            const meta = TIER_ICONS[key] || { icon: "📊", label: key };
            return (
              <div key={key} className="rounded-xl bg-secondary/30 border border-border p-5 text-center">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <span className={`w-2.5 h-2.5 rounded-full ${tier.ready ? "bg-success" : "bg-destructive"}`} />
                  <span className="text-lg">{meta.icon}</span>
                </div>
                <h4 className="text-sm font-bold text-foreground mb-1">{meta.label}</h4>
                <p className="text-xs text-muted-foreground mb-2">{(tier.companies || []).join(", ")}</p>
                <p className="text-xs text-foreground/60">{tier.notes}</p>
              </div>
            );
          })}
        </div>

        {/* Package */}
        {data.estimated_package_range && (
          <div className="rounded-xl border border-primary/30 p-5 text-center mb-8" style={{ background: "hsl(var(--primary) / 0.05)" }}>
            <span className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground">Estimated Package</span>
            <p className="text-xl font-extrabold text-primary mt-1">{data.estimated_package_range}</p>
          </div>
        )}

        {/* Actions */}
        {data.action_items && data.action_items.length > 0 && (
          <div>
            <h3 className="text-sm font-bold text-foreground mb-3">🎯 Top Actions</h3>
            <ol className="space-y-2">
              {data.action_items.map((a, i) => (
                <li key={i} className="flex items-start gap-3 text-sm text-muted-foreground">
                  <span className="w-6 h-6 rounded-full bg-primary/10 text-primary text-xs font-bold flex items-center justify-center flex-shrink-0">{i + 1}</span>
                  {a}
                </li>
              ))}
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};

export default ConfidencePanel;
