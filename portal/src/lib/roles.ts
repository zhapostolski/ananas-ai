import type { Role, Department } from "@/types";

/**
 * Role -> Departments the user can access.
 */
export const ROLE_DEPARTMENTS: Record<Role, Department[]> = {
  super_admin: ["marketing", "commercial", "finance", "logistics", "executive", "customer_experience", "hr"],
  executive: ["marketing", "commercial", "finance", "logistics", "executive", "customer_experience", "hr"],
  marketing_head: ["marketing"],
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
  cx_head: ["customer_experience", "marketing"],
  cx_team: ["customer_experience"],
  hr_head: ["hr", "executive"],
  hr: ["hr"],
};

/**
 * Role -> Marketing sub-modules allowed.
 * If not listed here, full marketing access is assumed for the dept.
 */
export const MARKETING_MODULE_ACCESS: Partial<
  Record<Role, string[]>
> = {
  performance_marketer: ["performance", "overview"],
  crm_specialist: ["crm", "overview"],
  content_brand: ["influencers", "overview"],
  marketing_ops: ["ops", "performance", "crm", "reputation", "overview"],
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
 * Roles that can access the admin area (user management).
 */
export const ADMIN_ROLES: Role[] = [
  "super_admin",
  "executive",
  "marketing_head",
  "finance_head",
  "logistics_head",
  "cx_head",
  "commercial_head",
  "hr_head",
];

/**
 * Roles that can invite new users.
 */
export const CAN_INVITE_ROLES: Role[] = ["super_admin", "executive"];

/**
 * Roles that can change other users' roles.
 */
export const CAN_CHANGE_ROLES: Role[] = [
  "super_admin",
  "executive",
  "marketing_head",
  "finance_head",
  "logistics_head",
  "cx_head",
  "commercial_head",
  "hr_head",
];

/**
 * Roles that can send platform notifications.
 */
export const CAN_SEND_NOTIFICATIONS_ROLES: Role[] = [
  "super_admin",
  "executive",
  "marketing_head",
  "finance_head",
  "logistics_head",
  "cx_head",
  "commercial_head",
  "hr_head",
];

/**
 * HR roles that can manage HR access delegation.
 */
export const HR_ROLES: Role[] = ["super_admin", "executive", "hr_head", "hr"];

export function isAdminRole(role: Role): boolean {
  return ADMIN_ROLES.includes(role);
}

export function canInvite(role: Role): boolean {
  return CAN_INVITE_ROLES.includes(role);
}

export function canChangeRoles(role: Role): boolean {
  return CAN_CHANGE_ROLES.includes(role);
}

export function canSendNotifications(role: Role): boolean {
  return CAN_SEND_NOTIFICATIONS_ROLES.includes(role);
}

/**
 * Human-readable role labels.
 */
export const ROLE_LABELS: Record<Role, string> = {
  super_admin: "Super Admin",
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
  cx_head: "CX Head",
  cx_team: "CX Team",
  hr_head: "HR Head",
  hr: "HR",
};
