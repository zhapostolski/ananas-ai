import type { Role, Department } from "@/types";

/**
 * Role -> Departments the user can access.
 */
export const ROLE_DEPARTMENTS: Record<Role, Department[]> = {
  executive: ["marketing", "commercial", "finance", "logistics"],
  marketing_head: ["marketing", "commercial"],
  performance_marketer: ["marketing"],
  crm_specialist: ["marketing"],
  content_brand: ["marketing"],
  marketing_ops: ["marketing"],
  commercial_head: ["commercial", "marketing"],
  commercial_3p: ["commercial"],
  commercial_1p: ["commercial"],
  finance_head: ["finance", "marketing", "commercial", "logistics"],
  finance_team: ["finance"],
  logistics_head: ["logistics", "commercial"],
  logistics_team: ["logistics"],
  hr: [],
};

/**
 * Role -> Marketing sub-modules allowed.
 * If not listed here, full marketing access is assumed for the dept.
 */
export const MARKETING_MODULE_ACCESS: Partial<
  Record<Role, string[]>
> = {
  performance_marketer: ["performance", "brief"],
  crm_specialist: ["crm", "brief"],
  content_brand: ["influencers", "brief"],
  marketing_ops: ["ops", "performance", "crm", "reputation", "brief"],
};

export function canAccessDepartment(role: Role, dept: Department): boolean {
  return ROLE_DEPARTMENTS[role]?.includes(dept) ?? false;
}

export function canAccessMarketingModule(
  role: Role,
  module: string
): boolean {
  const restricted = MARKETING_MODULE_ACCESS[role];
  if (!restricted) return true; // no restriction = full access
  return restricted.includes(module);
}

/**
 * Human-readable role labels.
 */
export const ROLE_LABELS: Record<Role, string> = {
  executive: "Executive",
  marketing_head: "Marketing Head",
  performance_marketer: "Performance Marketer",
  crm_specialist: "CRM Specialist",
  content_brand: "Content & Brand",
  marketing_ops: "Marketing Ops",
  commercial_head: "Commercial Head",
  commercial_3p: "Commercial Manager (3P)",
  commercial_1p: "Commercial Manager (1P)",
  finance_head: "Finance Head",
  finance_team: "Finance Team",
  logistics_head: "Logistics Head",
  logistics_team: "Logistics Team",
  hr: "HR",
};
