import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { User } from "@/types";
import { Rocket, Sparkles, FileText, Brain } from "lucide-react";

interface AuthPageProps {
  onLogin: (user: User) => void;
}

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const AuthPage = ({ onLogin }: AuthPageProps) => {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (mode === "login") {
        const res = await fetch(`${API_BASE}/login?email=${encodeURIComponent(email)}`, { method: "POST" });
        const data = await res.json();
        if (data.success) {
          onLogin({ user_id: data.user_id, name: data.name, email: data.email });
        } else {
          setError("Account not found. Please register first.");
        }
      } else {
        if (!name.trim()) { setError("Please enter your name."); setLoading(false); return; }
        const res = await fetch(`${API_BASE}/create-user?name=${encodeURIComponent(name)}&email=${encodeURIComponent(email)}`, { method: "POST" });
        const data = await res.json();
        onLogin({ user_id: data.user_id, name: data.name, email: data.email });
      }
    } catch {
      setError("Connection failed. Is the backend running?");
    } finally {
      setLoading(false);
    }
  };

  const features = [
    { icon: FileText, label: "8-Agent Analysis Pipeline" },
    { icon: Brain, label: "AI-Powered Optimization" },
    { icon: Sparkles, label: "Smart Interview Prep" },
    { icon: Rocket, label: "Placement Confidence Score" },
  ];

  return (
    <div className="min-h-screen flex items-center justify-center p-4" style={{ background: "var(--gradient-hero)" }}>
      {/* Decorative orbs */}
      <div className="fixed top-20 left-20 w-72 h-72 rounded-full opacity-20 blur-[100px]" style={{ background: "hsl(var(--primary))" }} />
      <div className="fixed bottom-20 right-20 w-96 h-96 rounded-full opacity-10 blur-[120px]" style={{ background: "hsl(var(--accent))" }} />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md relative z-10"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center gap-2 mb-3">
            <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
              <Rocket className="w-5 h-5 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-bold text-foreground">AI Placement Cell</h1>
          </div>
          <p className="text-sm text-muted-foreground">Multi-agent resume analysis platform</p>
        </div>

        {/* Feature pills */}
        <div className="flex flex-wrap justify-center gap-2 mb-8">
          {features.map((f) => (
            <span key={f.label} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground border border-border">
              <f.icon className="w-3 h-3 text-primary" />
              {f.label}
            </span>
          ))}
        </div>

        {/* Auth card */}
        <div className="glass-card rounded-2xl p-8">
          {/* Tabs */}
          <div className="flex mb-6 rounded-xl bg-secondary p-1">
            {(["login", "register"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => { setMode(tab); setError(""); }}
                className={`flex-1 py-2.5 text-sm font-semibold rounded-lg transition-all duration-200 ${
                  mode === tab
                    ? "bg-primary text-primary-foreground shadow-lg"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {tab === "login" ? "Sign In" : "Register"}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {error && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="mb-4 px-4 py-3 rounded-lg text-sm font-medium bg-destructive/10 text-destructive border border-destructive/20"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} className="space-y-4">
            <AnimatePresence mode="wait">
              {mode === "register" && (
                <motion.div
                  key="name"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                >
                  <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Full Name</label>
                  <input
                    type="text"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="Enter your name"
                    className="w-full px-4 py-3 rounded-xl bg-input border border-border text-foreground placeholder:text-muted-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
                  />
                </motion.div>
              )}
            </AnimatePresence>

            <div>
              <label className="block text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
                className="w-full px-4 py-3 rounded-xl bg-input border border-border text-foreground placeholder:text-muted-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl text-sm font-bold text-primary-foreground transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: loading ? "hsl(var(--muted))" : "var(--gradient-primary)", boxShadow: loading ? "none" : "var(--shadow-glow)" }}
            >
              {loading ? "Connecting..." : mode === "login" ? "Sign In" : "Create Account"}
            </button>
          </form>


        </div>
      </motion.div>
    </div>
  );
};

export default AuthPage;
