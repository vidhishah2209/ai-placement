import { ImprovedResume } from "@/types";
import { Download, Printer, CheckCircle, XCircle } from "lucide-react";
// @ts-ignore
import html2pdf from "html2pdf.js";

interface ResumePanelProps {
  data: ImprovedResume;
  supervisorPassed: boolean;
}

const ResumePanel = ({ data, supervisorPassed }: ResumePanelProps) => {
  const handleDownloadJSON = () => {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url; a.download = "improved_resume.json"; a.click();
    URL.revokeObjectURL(url);
  };

  const handleExportPDF = () => {
    const element = document.getElementById('resume-pdf');
    if (!element) return;
    
    const opt = {
      margin: 0,
      filename: `${(data.name || 'Resume').replace(/\s+/g, '_')}_Resume.pdf`,
      image: { type: 'jpeg' as const, quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' as const }
    };
    
    html2pdf().set(opt).from(element).save();
  };

  return (
    <div className="animate-fade-in">
      <h1 className="text-2xl font-bold text-foreground mb-1">Improved Resume</h1>
      <p className="text-sm text-muted-foreground mb-6">AI-enhanced version with better action verbs and metrics.</p>

      <div className="glass-card rounded-2xl p-6">
        {/* Export bar */}
        <div className="flex gap-3 mb-5">
          <button onClick={handleDownloadJSON} className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-border text-sm font-medium text-foreground hover:bg-primary/10 hover:border-primary/30 hover:text-primary transition-all">
            <Download className="w-4 h-4" /> Download JSON
          </button>
          <button onClick={handleExportPDF} className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-bold text-primary-foreground shadow-lg transition-all duration-200" style={{ background: "var(--gradient-primary)", boxShadow: "var(--shadow-glow)" }}>
            <Printer className="w-4 h-4" /> Export as PDF
          </button>
        </div>

        {/* Supervisor */}
        <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-xs font-bold mb-6 ${
          supervisorPassed ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive"
        }`}>
          {supervisorPassed ? <CheckCircle className="w-3.5 h-3.5" /> : <XCircle className="w-3.5 h-3.5" />}
          {supervisorPassed ? "Supervisor Approved — No hallucinations detected" : "Supervisor flagged issues"}
        </div>

        {/* Changes */}
        {data.changes_made && data.changes_made.length > 0 && (
          <div className="mb-6">
            <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground mb-3">🔄 Changes Made</h3>
            <ul className="space-y-1.5">
              {data.changes_made.map((c, i) => (
                <li key={i} className="flex items-start gap-2 text-sm text-muted-foreground">
                  <span className="w-1.5 h-1.5 mt-1.5 rounded-full bg-primary flex-shrink-0" />
                  {c}
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Summary */}
        {data.summary && (
          <div className="rounded-xl bg-secondary/30 border border-border p-5 mb-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary mb-2">Professional Summary</h3>
            <p className="text-sm text-foreground/80 leading-relaxed">{data.summary}</p>
          </div>
        )}

        {/* Projects */}
        {data.projects && data.projects.length > 0 && (
          <div className="rounded-xl bg-secondary/30 border border-border p-5 mb-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary mb-4">Projects</h3>
            <div className="space-y-5">
              {data.projects.map((p, i) => (
                <div key={i} className={i < data.projects.length - 1 ? "pb-5 border-b border-border" : ""}>
                  <h5 className="text-sm font-bold text-foreground">{p.title}</h5>
                  {p.description && <p className="text-xs text-muted-foreground mt-1">{p.description}</p>}
                  <ul className="mt-2 space-y-1">
                    {(p.bullets || []).map((b, j) => (
                      <li key={j} className="flex items-start gap-2 text-sm text-foreground/70">
                        <span className="text-primary mt-0.5">▸</span> {b}
                      </li>
                    ))}
                  </ul>
                  {p.tech_stack && p.tech_stack.length > 0 && (
                    <div className="flex flex-wrap gap-1.5 mt-2">
                      {p.tech_stack.map((t) => (
                        <span key={t} className="px-2 py-0.5 rounded-md text-[10px] font-medium bg-primary/10 text-primary border border-primary/20">{t}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Experience */}
        {data.experience && data.experience.length > 0 && (
          <div className="rounded-xl bg-secondary/30 border border-border p-5">
            <h3 className="text-xs font-bold uppercase tracking-wider text-primary mb-4">Experience</h3>
            <div className="space-y-5">
              {data.experience.map((e, i) => (
                <div key={i} className={i < data.experience.length - 1 ? "pb-5 border-b border-border" : ""}>
                  <h5 className="text-sm font-bold text-foreground">{e.role} — {e.company}</h5>
                  <p className="text-xs text-muted-foreground mt-0.5">{e.duration}</p>
                  <ul className="mt-2 space-y-1">
                    {(e.bullets || []).map((b, j) => (
                      <li key={j} className="flex items-start gap-2 text-sm text-foreground/70">
                        <span className="text-primary mt-0.5">▸</span> {b}
                      </li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Hidden PDF Production Template */}
      <div style={{ display: 'none' }}>
        <div id="resume-pdf" style={{ width: '8.5in', minHeight: '11in', padding: '0.6in 0.8in', background: '#ffffff', color: '#000000', fontFamily: 'Arial, sans-serif', fontSize: '11pt', lineHeight: '1.4', boxSizing: 'border-box' }}>
          {/* Header */}
          <div style={{ textAlign: 'center', marginBottom: '16px', borderBottom: '1px solid #cccccc', paddingBottom: '12px' }}>
            <h1 style={{ fontSize: '24pt', fontWeight: 'bold', margin: '0 0 6px 0', color: '#111111', textTransform: 'uppercase' }}>{data.name || "YOUR NAME"}</h1>
            <div style={{ fontSize: '10pt', color: '#444444', display: 'flex', justifyContent: 'center', gap: '12px', flexWrap: 'wrap' }}>
              {data.email && <span>{data.email}</span>}
              {data.phone && <span>• {data.phone}</span>}
              {data.linkedin && <span>• {data.linkedin.replace('https://', '').replace('www.', '')}</span>}
              {data.github && <span>• {data.github.replace('https://', '').replace('www.', '')}</span>}
            </div>
          </div>

          {/* Summary */}
          {data.summary && (
            <div style={{ marginBottom: '14px' }}>
              <p style={{ margin: 0, textAlign: 'justify' }}>{data.summary}</p>
            </div>
          )}

          {/* Education */}
          {data.education && data.education.length > 0 && (
            <div style={{ marginBottom: '14px' }}>
              <h2 style={{ fontSize: '12pt', fontWeight: 'bold', margin: '0 0 6px 0', textTransform: 'uppercase', borderBottom: '1px solid #eeeeee', color: '#222222' }}>Education</h2>
              {data.education.map((ed, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <div>
                    <div style={{ fontWeight: 'bold' }}>{ed.institution}</div>
                    <div style={{ fontStyle: 'italic', fontSize: '10pt' }}>{ed.degree}</div>
                  </div>
                  <div style={{ textAlign: 'right', fontSize: '10pt' }}>
                    <div>{ed.location || ""}</div>
                    <div>{ed.year || ""} {ed.gpa ? `| GPA: ${ed.gpa}` : ''}</div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Skills */}
          {data.skills && (Object.keys(data.skills).length > 0) && (
            <div style={{ marginBottom: '14px' }}>
              <h2 style={{ fontSize: '12pt', fontWeight: 'bold', margin: '0 0 6px 0', textTransform: 'uppercase', borderBottom: '1px solid #eeeeee', color: '#222222' }}>Technical Skills</h2>
              <div style={{ display: 'grid', gridTemplateColumns: '120px 1fr', gap: '4px', fontSize: '10pt' }}>
                {Object.entries(data.skills).map(([category, list]) => {
                  if (!list || (Array.isArray(list) && list.length === 0)) return null;
                  const formattedCategory = category.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                  const items = Array.isArray(list) ? list.join(', ') : '';
                  return (
                    <div key={category} style={{ display: 'contents' }}>
                      <div style={{ fontWeight: 'bold' }}>{formattedCategory}:</div>
                      <div>{items}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Experience */}
          {data.experience && data.experience.length > 0 && (
            <div style={{ marginBottom: '14px' }}>
              <h2 style={{ fontSize: '12pt', fontWeight: 'bold', margin: '0 0 6px 0', textTransform: 'uppercase', borderBottom: '1px solid #eeeeee', color: '#222222' }}>Experience</h2>
              {data.experience.map((e, i) => (
                <div key={i} style={{ marginBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <div style={{ fontWeight: 'bold' }}>{e.role}</div>
                    <div style={{ fontSize: '10pt' }}>{e.duration}</div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline', fontStyle: 'italic', fontSize: '10pt', marginBottom: '4px' }}>
                    <div>{e.company}</div>
                    <div>{e.location || ""}</div>
                  </div>
                  {e.bullets && e.bullets.length > 0 && (
                    <ul style={{ margin: '0 0 0 16px', padding: 0, fontSize: '10pt' }}>
                      {e.bullets.map((b, j) => (
                        <li key={j} style={{ marginBottom: '3px', textAlign: 'justify' }}>{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Projects */}
          {data.projects && data.projects.length > 0 && (
            <div style={{ marginBottom: '14px' }}>
              <h2 style={{ fontSize: '12pt', fontWeight: 'bold', margin: '0 0 6px 0', textTransform: 'uppercase', borderBottom: '1px solid #eeeeee', color: '#222222' }}>Projects</h2>
              {data.projects.map((p, i) => (
                <div key={i} style={{ marginBottom: '8px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
                    <div>
                      <span style={{ fontWeight: 'bold' }}>{p.title}</span>
                      {p.tech_stack && p.tech_stack.length > 0 && (
                        <span style={{ fontStyle: 'italic', fontSize: '10pt' }}> | {p.tech_stack.join(', ')}</span>
                      )}
                    </div>
                    {p.date && <div style={{ fontSize: '10pt' }}>{p.date}</div>}
                  </div>
                  {p.description && <div style={{ fontStyle: 'italic', fontSize: '10pt', marginBottom: '2px' }}>{p.description}</div>}
                  {p.bullets && p.bullets.length > 0 && (
                    <ul style={{ margin: '4px 0 0 16px', padding: 0, fontSize: '10pt' }}>
                      {p.bullets.map((b, j) => (
                        <li key={j} style={{ marginBottom: '3px', textAlign: 'justify' }}>{b}</li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Extracurricular / Achievements */}
          {data.achievements && data.achievements.length > 0 && (
            <div>
              <h2 style={{ fontSize: '12pt', fontWeight: 'bold', margin: '0 0 6px 0', textTransform: 'uppercase', borderBottom: '1px solid #eeeeee', color: '#222222' }}>Achievements</h2>
              <ul style={{ margin: '0 0 0 16px', padding: 0, fontSize: '10pt' }}>
                {data.achievements.map((a, i) => (
                  <li key={i} style={{ marginBottom: '3px' }}>{a}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResumePanel;
