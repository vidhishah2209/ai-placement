export interface User {
  user_id: string;
  name: string;
  email: string;
  target_role?: string;
}

export interface ATSBreakdownItem {
  score: number;
  max: number;
  feedback: string;
}

export interface ATSScore {
  total_score: number;
  reasoning: string;
  breakdown: Record<string, ATSBreakdownItem>;
  strengths: string[];
  weaknesses: string[];
}

export interface SkillGaps {
  missing_critical: string[];
  missing_recommended: string[];
  frameworks_to_learn: {
    name: string;
    category: string;
    reason: string;
  }[];
  priority_actions: {
    skill: string;
    priority: string;
    reason: string;
    resource_hint?: string;
  }[];
}

export interface ImprovedResume {
  name?: string;
  email?: string;
  phone?: string;
  linkedin?: string;
  github?: string;
  summary: string;
  changes_made: string[];
  education?: {
    institution: string;
    degree: string;
    location?: string;
    year?: string;
    gpa?: string;
  }[];
  skills?: Record<string, string[]>;
  projects: {
    title: string;
    description: string;
    bullets: string[];
    tech_stack: string[];
    date?: string;
  }[];
  experience: {
    role: string;
    company: string;
    duration: string;
    location?: string;
    bullets: string[];
  }[];
  achievements?: string[];
}

export interface InterviewQuestion {
  id: number;
  question: string;
  category: string;
  difficulty: string;
  context: string;
  model_answer: {
    intro: string;
    core: string;
    example: string;
    conclusion: string;
  };
  follow_up: string;
}

export interface InterviewQNA {
  questions: InterviewQuestion[];
  estimated_difficulty: string;
  interview_tips: string[];
}

export interface TierReadiness {
  ready: boolean;
  companies: string[];
  notes: string;
}

export interface ConfidenceScore {
  confidence_percentage: number;
  summary: string;
  tier_readiness: {
    service_based: TierReadiness;
    mid_tier_product: TierReadiness;
    top_product: TierReadiness;
  };
  estimated_package_range: string;
  action_items: string[];
}

export interface AnalysisResponse {
  parsed_resume: Record<string, unknown>;
  ats_score: ATSScore;
  skill_gaps: SkillGaps;
  improved_resume: ImprovedResume;
  supervisor_passed: boolean;
  interview_qna: InterviewQNA;
  confidence_score: ConfidenceScore;
  errors: string[];
}

export type SectionId = 'upload' | 'ats' | 'skills' | 'resume' | 'interview' | 'confidence';
