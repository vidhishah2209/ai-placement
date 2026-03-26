import { Upload, BarChart3, Target, FileEdit, Mic, Rocket, LogOut } from "lucide-react";
import { SectionId, User } from "@/types";

interface SidebarProps {
  user: User;
  activeSection: SectionId;
  hasResults: boolean;
  onNavigate: (section: SectionId) => void;
  onLogout: () => void;
}

const NAV_ITEMS: { id: SectionId; icon: typeof Upload; label: string; requiresResults?: boolean }[] = [
  { id: "upload", icon: Upload, label: "Upload Resume" },
  { id: "ats", icon: BarChart3, label: "ATS Score", requiresResults: true },
  { id: "skills", icon: Target, label: "Skill Gaps", requiresResults: true },
  { id: "resume", icon: FileEdit, label: "Improved Resume", requiresResults: true },
  { id: "interview", icon: Mic, label: "Interview Prep", requiresResults: true },
  { id: "confidence", icon: Rocket, label: "Confidence Score", requiresResults: true },
];

const AppSidebar = ({ user, activeSection, hasResults, onNavigate, onLogout }: SidebarProps) => {
  return (
    <aside className="fixed top-0 left-0 h-screen w-[260px] flex flex-col bg-sidebar z-50 border-r border-sidebar-border">
      {/* Header */}
      <div className="px-6 py-6 border-b border-sidebar-border">
        <div className="flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center" style={{ background: "var(--gradient-primary)" }}>
            <Rocket className="w-4 h-4 text-primary-foreground" />
          </div>
          <div>
            <h2 className="text-sm font-bold text-sidebar-accent-foreground">AI Placement Cell</h2>
            <p className="text-[11px] text-sidebar-foreground/50">Resume Analysis Platform</p>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        <p className="px-3 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/30">Main</p>
        {NAV_ITEMS.slice(0, 1).map((item) => {
          const isActive = activeSection === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                isActive
                  ? "bg-primary text-primary-foreground shadow-lg"
                  : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          );
        })}

        <p className="px-3 mt-5 mb-2 text-[10px] font-semibold uppercase tracking-widest text-sidebar-foreground/30">Analysis Results</p>
        {NAV_ITEMS.slice(1).map((item) => {
          const isActive = activeSection === item.id;
          const disabled = item.requiresResults && !hasResults;
          return (
            <button
              key={item.id}
              onClick={() => !disabled && onNavigate(item.id)}
              disabled={disabled}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                disabled
                  ? "text-sidebar-foreground/25 cursor-not-allowed"
                  : isActive
                  ? "bg-primary text-primary-foreground shadow-lg"
                  : "text-sidebar-foreground/60 hover:text-sidebar-foreground hover:bg-sidebar-accent"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-4 py-4 border-t border-sidebar-border">
        <div className="flex items-center gap-3 mb-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold text-primary-foreground" style={{ background: "var(--gradient-primary)" }}>
            {user.name?.[0]?.toUpperCase() || "U"}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-xs font-semibold text-sidebar-accent-foreground truncate">{user.name}</p>
            <p className="text-[10px] text-sidebar-foreground/40 truncate">{user.email}</p>
          </div>
        </div>
        <button
          onClick={onLogout}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-medium text-destructive/70 hover:text-destructive hover:bg-destructive/10 transition-all"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default AppSidebar;
