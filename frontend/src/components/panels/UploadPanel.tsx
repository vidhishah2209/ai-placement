import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Upload, FileText, Rocket, Check, Loader2, AlertCircle } from "lucide-react";
import { AnalysisResponse, SectionId } from "@/types";

const ROLES = [
  "Software Engineer", "Frontend Developer", "Backend Developer",
  "Data Analyst", "Data Scientist", "Full Stack Developer",
  "DevOps Engineer", "Machine Learning Engineer", "Custom Role",
];

const STEPS = [
  "Parsing resume...", "ATS scoring...", "Analyzing skill gaps...",
  "Rewriting resume...", "Supervisor checking...", "Saving to database...",
  "Generating interview Q&A...", "Calculating confidence...",
];

const QUIZ_QUESTIONS = [
  {
    q: "What does ATS stand for in recruitment?",
    options: ["Automated Tracking System", "Applicant Tracking System", "Application Testing Software"],
    ans: 1,
    exp: "Applicant Tracking System. It's software used by 99% of top companies to filter resumes automatically."
  },
  {
    q: "Which resume format is preferred by top Indian tech product companies?",
    options: ["2-page colorful design", "1-page single column", "Multi-page detailed portfolio"],
    ans: 1,
    exp: "A clean, 1-page single-column format is easiest for both ATS parsers and busy recruiters to read."
  },
  {
    q: "What does the 'R' in the STAR interview method stand for?",
    options: ["Reaction", "Resource", "Result"],
    ans: 2,
    exp: "STAR = Situation, Task, Action, Result. Recruiters look for the tangible 'Result' or impact of your work."
  },
  {
    q: "Which skill is most heavily tested in top Indian PBCs rounds?",
    options: ["HTML & CSS", "System Design & DSA", "Agile & Scrum"],
    ans: 1,
    exp: "Top product companies prioritize core problem-solving (DSA) and scalable architecture (System Design)."
  },
  {
    q: "What is the ideal bullet point length in a tech resume?",
    options: ["1-2 lines with a metric", "A massive detailed paragraph", "Just 2-3 words"],
    ans: 0,
    exp: "Bullets should be 1-2 lines maximum and MUST include a quantifiable metric (e.g., 'improved speed by 20%')."
  },
  {
    q: "Should you include a photo on your software engineering resume?",
    options: ["Yes, always", "No, it wastes space & breaks ATS", "Only if it's professional"],
    ans: 1,
    exp: "No. ATS parsers struggle with images, and it wastes valuable space that should be used for projects and skills."
  },
  {
    q: "Which of the following is considered an 'Action Verb'?",
    options: ["Helped with", "Orchestrated", "Worked on"],
    ans: 1,
    exp: "Action verbs like 'Orchestrated', 'Architected', or 'Engineered' show ownership and drive."
  },
  {
    q: "What is the primary focus of an 'HR/Behavioral' interview?",
    options: ["Coding algorithms", "Cultural fit & team skills", "Database schemas"],
    ans: 1,
    exp: "HR rounds test your communication, emotional intelligence, and ability to handle workplace conflicts."
  },
  {
    q: "How many projects ideally belong on a fresher's resume?",
    options: ["1 massive project", "2-3 high quality projects", "7-8 small projects"],
    ans: 1,
    exp: "Quality over quantity. 2-3 deep, metric-driven projects are vastly superior to 8 simple 'todo list' clones."
  },
  {
    q: "What does CTC stand for in Indian job offers?",
    options: ["Cost to Company", "Cash to Candidate", "Corporate Training Cost"],
    ans: 0,
    exp: "CTC stands for Cost to Company. Note: your actual in-hand salary will always be lower than your CTC."
  },
  {
    q: "Is it okay to put '8/10' or 'Expert' next to your skills on a resume?",
    options: ["Yes, it shows confidence", "No, it's subjective and risky", "Only for languages you know well"],
    ans: 1,
    exp: "Never rate skills. It's subjective, and claiming 'Expertise' invites brutal grilling from interviewers."
  },
  {
    q: "Which section typically goes FIRST on a student/fresher resume?",
    options: ["Work Experience", "Education", "Hobbies"],
    ans: 1,
    exp: "For freshers, Education comes first. Once you have 1-2 years of experience, Work Experience moves to the top."
  },
  {
    q: "What happens if your resume implies a skill you can't actually explain?",
    options: ["They won't ask about it", "It creates a negative impression", "It doesn't matter"],
    ans: 1,
    exp: "Lying or exaggerating is a massive red flag. Anything on your resume is fair game for deep technical questions."
  },
  {
    q: "Why should you include your GitHub link?",
    options: ["To show you have an account", "To provide proof of code quality", "Because everyone does it"],
    ans: 1,
    exp: "Recruiters use GitHub to verify that your projects are real, check your commit history, and review your code structure."
  },
  {
    q: "How soon should you send a 'Thank You' email after an interview?",
    options: ["Within 24 hours", "After 1 week", "Never"],
    ans: 0,
    exp: "Within 24 hours shows professionalism, keeps you fresh in their mind, and reiterates your strong interest in the role."
  }
];

interface UploadPanelProps {
  userId: string;
  onAnalysisComplete: (data: AnalysisResponse) => void;
  onNavigate: (section: SectionId) => void;
}

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const UploadPanel = ({ userId, onAnalysisComplete, onNavigate }: UploadPanelProps) => {
  const [file, setFile] = useState<File | null>(null);
  const [targetRole, setTargetRole] = useState("Software Engineer");
  const [customRole, setCustomRole] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState(0);
  const [qIndex, setQIndex] = useState(0);
  const [selectedOpt, setSelectedOpt] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (loading && selectedOpt !== null) {
      const timer = setTimeout(() => {
        setQIndex((prev) => (prev + 1) % QUIZ_QUESTIONS.length);
        setSelectedOpt(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [loading, selectedOpt]);

  const handleDragOver = (e: React.DragEvent) => e.preventDefault();
  
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files?.[0]) setFile(e.dataTransfer.files[0]);
  };
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) setFile(e.target.files[0]);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setLoadingStep(0);
    setQIndex(0);
    setSelectedOpt(null);

    const stepInterval = setInterval(() => {
      setLoadingStep((s) => Math.min(s + 1, 7));
    }, 4000);

    try {
      const fd = new FormData();
      fd.append("file", file);
      fd.append("user_id", userId);
      fd.append("target_role", targetRole === "Custom Role" ? customRole : targetRole);

      const res = await fetch(`${API_BASE}/analyze-resume/`, { method: "POST", body: fd });
      const data = await res.json();
      
      if (data.job_id) {
        // Start Polling
        const pollInterval = window.setInterval(async () => {
          try {
            const statusRes = await fetch(`${API_BASE}/analyze-status/${data.job_id}`);
            const statusData = await statusRes.json();
            
            if (statusData.status === "completed") {
              window.clearInterval(pollInterval);
              clearInterval(stepInterval);
              setLoading(false);
              onAnalysisComplete(statusData.data);
            } else if (statusData.status === "error") {
              window.clearInterval(pollInterval);
              clearInterval(stepInterval);
              setLoading(false);
              setError(statusData.message || "Analysis failed on the server.");
            }
          } catch (err) {
            // Keep trying if network blips
          }
        }, 3000);
      } else {
        // Fallback for sync
        clearInterval(stepInterval);
        setLoading(false);
        onAnalysisComplete(data);
      }
    } catch {
      clearInterval(stepInterval);
      setLoading(false);
      setError("Analysis failed. Please check your connection and try again.");
    }
  };

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Upload Resume</h1>
      <p className="text-sm text-muted-foreground mb-6">Upload your resume PDF and select a target role to run the 8-agent analysis pipeline.</p>

      <div className="glass-card rounded-2xl p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-[1fr_280px] gap-6">
          {/* File zone */}
          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">Resume File</label>
            <div
              onClick={() => fileRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className={`relative flex flex-col items-center justify-center h-44 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 ${
                file
                  ? "border-success/50 bg-success/5"
                  : "border-border hover:border-primary/50 hover:bg-primary/5"
              }`}
            >
              {file ? (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                    <Check className="w-5 h-5 text-success" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-foreground">{file.name}</p>
                    <p className="text-xs text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
              ) : (
                <>
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mb-3">
                    <FileText className="w-6 h-6 text-primary/60" />
                  </div>
                  <p className="text-sm text-muted-foreground">Drop PDF or click to browse</p>
                </>
              )}
              <input ref={fileRef} type="file" accept=".pdf" onChange={handleFileChange} className="hidden" />
            </div>
          </div>

          {/* Role select */}
          <div>
            <label className="block text-[11px] font-semibold uppercase tracking-wider text-muted-foreground mb-3">Target Role</label>
            <select
              value={targetRole}
              onChange={(e) => setTargetRole(e.target.value)}
              className="w-full px-4 py-3 rounded-xl bg-input border border-border text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-primary/50 appearance-none cursor-pointer"
            >
              {ROLES.map((r) => <option key={r} value={r}>{r}</option>)}
            </select>

            <AnimatePresence>
              {targetRole === "Custom Role" && (
                <motion.input
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  exit={{ opacity: 0, height: 0 }}
                  type="text"
                  value={customRole}
                  onChange={(e) => setCustomRole(e.target.value)}
                  placeholder="e.g. Blockchain Developer"
                  className="w-full mt-3 px-4 py-3 rounded-xl bg-input border border-border text-foreground text-sm placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              )}
            </AnimatePresence>
          </div>
        </div>

        {/* Buttons row */}
        <div className="flex gap-3 mt-6">
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className="flex-1 py-4 rounded-xl text-sm font-bold text-primary-foreground transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            style={{ background: !file || loading ? "hsl(var(--muted))" : "var(--gradient-primary)", boxShadow: !file || loading ? "none" : "var(--shadow-glow)" }}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Running Pipeline...
              </>
            ) : (
              <>
                <Rocket className="w-4 h-4" />
                Analyze Resume
              </>
            )}
          </button>
        </div>
      </div>

      {/* Loading card */}
      <AnimatePresence>
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="glass-card rounded-2xl p-6"
          >
            <div className="flex items-center gap-3 mb-5">
              <div className="w-10 h-10 rounded-full border-2 border-primary border-t-transparent" style={{ animation: "spin 0.8s linear infinite" }} />
              <div>
                <p className="text-sm font-bold text-foreground">Running 8-Agent Pipeline</p>
                <p className="text-xs text-muted-foreground">This may take 30–60 seconds. We are actively analyzing every line of your resume.</p>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2 border-r border-border/50 pr-4">
                {STEPS.map((step, i) => (
                  <div key={step} className={`flex items-center gap-3 py-1 text-sm transition-all ${
                    i < loadingStep ? "text-success" : i === loadingStep ? "text-primary font-semibold" : "text-muted-foreground/40"
                  }`}>
                    <span className="w-5 text-center">
                      {i < loadingStep ? "✅" : i === loadingStep ? "⏳" : "○"}
                    </span>
                    {step}
                  </div>
                ))}
              </div>
              
              <div className="flex flex-col p-5 bg-secondary/30 rounded-xl relative overflow-hidden h-[220px]">
                <div className="absolute top-2 left-3 text-[10px] font-bold text-primary uppercase tracking-wider">Placement Quiz</div>
                
                <AnimatePresence mode="wait">
                  <motion.div
                    key={qIndex}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -20 }}
                    transition={{ duration: 0.3 }}
                    className="flex flex-col h-full w-full pt-4"
                  >
                    <p className="text-sm font-semibold text-foreground mb-3 leading-snug">
                      {QUIZ_QUESTIONS[qIndex].q}
                    </p>

                    {selectedOpt === null ? (
                      <div className="space-y-2 flex-1">
                        {QUIZ_QUESTIONS[qIndex].options.map((opt, i) => (
                          <button
                            key={i}
                            onClick={() => setSelectedOpt(i)}
                            className="w-full text-left px-3 py-2 rounded-lg text-xs font-medium bg-background border border-border hover:border-primary/50 hover:bg-primary/5 transition-colors"
                          >
                            {opt}
                          </button>
                        ))}
                      </div>
                    ) : (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`flex-1 p-3 rounded-lg border ${
                          selectedOpt === QUIZ_QUESTIONS[qIndex].ans
                            ? "bg-success/10 border-success/30"
                            : "bg-destructive/10 border-destructive/30"
                        }`}
                      >
                        <div className="flex items-center gap-2 mb-1.5">
                          {selectedOpt === QUIZ_QUESTIONS[qIndex].ans ? (
                            <Check className="w-4 h-4 text-success" />
                          ) : (
                            <AlertCircle className="w-4 h-4 text-destructive" />
                          )}
                          <span className={`text-xs font-bold ${selectedOpt === QUIZ_QUESTIONS[qIndex].ans ? "text-success" : "text-destructive"}`}>
                            {selectedOpt === QUIZ_QUESTIONS[qIndex].ans ? "Correct!" : "Incorrect"}
                          </span>
                        </div>
                        <p className="text-[11px] text-foreground leading-relaxed">
                          {QUIZ_QUESTIONS[qIndex].exp}
                        </p>
                        <div className="w-full h-1 bg-border rounded-full mt-3 overflow-hidden">
                          <motion.div 
                            initial={{ width: "0%" }}
                            animate={{ width: "100%" }}
                            transition={{ duration: 5, ease: "linear" }}
                            className="h-full bg-primary"
                          />
                        </div>
                      </motion.div>
                    )}
                  </motion.div>
                </AnimatePresence>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Error */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-4 glass-card rounded-xl p-4 border border-destructive/30"
          >
            <div className="flex items-center gap-2 text-destructive text-sm font-medium">
              <AlertCircle className="w-4 h-4" />
              {error}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default UploadPanel;
