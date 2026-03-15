export type Department =
  | "marketing"
  | "commercial"
  | "finance"
  | "logistics"
  | "executive"
  | "customer_experience";

export type MarketingModule =
  | "performance"
  | "crm"
  | "reputation"
  | "ops"
  | "influencers"
  | "brief";

export type Role =
  | "executive"
  | "marketing_head"
  | "performance_marketer"
  | "crm_specialist"
  | "content_brand"
  | "marketing_ops"
  | "commercial_head"
  | "commercial_3p"
  | "commercial_1p"
  | "finance_head"
  | "finance_team"
  | "logistics_head"
  | "logistics_team"
  | "cx_head"
  | "cx_team"
  | "hr";

export interface UserProfile {
  id: string;
  name: string;
  email: string;
  image?: string;
  role: Role;
  department: Department;
}

export interface AgentOutput {
  id: number;
  agent_id: string;
  run_at: string;
  status: "ok" | "error" | "skipped";
  output_json: Record<string, unknown> | null;
  summary_text: string | null;
  model_used: string;
  tokens_in: number;
  tokens_out: number;
  estimated_cost: number;
  duration_ms: number;
}

export interface NavItem {
  label: string;
  href: string;
  icon?: string;
  badge?: string;
  requiredRoles?: Role[];
}

export interface DeptSection {
  id: Department;
  label: string;
  icon: string;
  href: string;
  requiredRoles: Role[];
  children?: NavItem[];
}
