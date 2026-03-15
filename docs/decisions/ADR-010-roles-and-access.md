# ADR-010: Roles, Access Control, and User Profile System

**Date:** 2026-03-15
**Status:** Accepted
**Authors:** Platform team

---

## Context

The Ananas AI portal requires a structured access control system to ensure that agents and intelligence data are only visible to authorized users. At the same time, building user profiles and behavior tracking allows for personalization (overview card ordering by interest, favorite agents) and operational insight into how the platform is being used.

Phase 1 had no real enforcement: the sidebar rendered all modules regardless of role, and no routes were protected beyond basic authentication.

---

## Decision

### 1. Four-level access enforcement

Access is enforced at four levels:

| Level | Mechanism | Where |
|---|---|---|
| Authentication | NextAuth v5 + Microsoft Entra ID | middleware.ts |
| Department | `ROLE_DEPARTMENTS` map + middleware route guards | middleware.ts, layout redirects |
| Module | `MARKETING_MODULE_ACCESS` map + sidebar child filtering | sidebar.tsx |
| Admin | `ADMIN_ROLES` list + layout redirect | admin/layout.tsx |

The middleware handles department-level route protection at the edge. Module-level filtering happens in the sidebar (client-side) -- restricted modules are not rendered.

### 2. DB-first role resolution

On each sign-in, the JWT callback looks up the user's role from `portal.db portal_users.role` before falling back to the static `EMAIL_ROLE_MAP`. This allows admins to change roles via the admin panel without waiting for code deployments.

Priority: `portal.db role` > `EMAIL_ROLE_MAP` > `performance_marketer` (default)

### 3. Portal database (portal.db)

A separate SQLite database (`portal.db`) stores portal-specific data:

- `portal_users` -- user profiles, roles, preferences, interests
- `portal_role_invites` -- pre-assigned roles for users before first login
- `portal_page_views` -- page tracking for behavior analytics
- `portal_role_audit` -- audit trail for all role changes

This is separate from `ananas_ai.db` (agent outputs, read-only).

### 4. User profile system

Each user has a profile with:
- Avatar initials with selectable color
- Bio
- Interests (up to 10 topics from a fixed list)
- Favorite agents
- Preferences (theme, density, notification toggles)

Interests drive overview card personalization.

### 5. Role invite flow

Admins can pre-assign a role to an email before the user's first login. On first sign-in, the portal checks for a pending invite and applies it before creating the user record.

### 6. Admin pages

Two admin-only pages:
- `/admin/users` -- user table with inline role dropdown
- `/admin/users/invite` -- invite form (email + role)

Admin access is restricted to `executive` and `marketing_head` roles.

---

## Role Definitions

| Role | Department Access | Marketing Modules |
|---|---|---|
| executive | all | all |
| marketing_head | marketing | all |
| performance_marketer | marketing | performance, overview |
| crm_specialist | marketing | crm, overview |
| content_brand | marketing | influencers, overview |
| marketing_ops | marketing | ops, performance, crm, reputation, overview |
| commercial_head | commercial, marketing | all marketing |
| finance_head | finance, marketing, commercial, logistics | all marketing |
| finance_team | finance | none |
| logistics_head | logistics, commercial | none |
| logistics_team | logistics | none |
| cx_head | customer_experience, marketing | all marketing |
| cx_team | customer_experience | none |
| hr | none | none |

---

## Consequences

**Positive:**
- Fine-grained access control without a third-party identity provider extension
- DB-first roles allow runtime role changes without deployments
- User behavior tracking feeds into personalization without a separate analytics stack
- Audit trail for all role changes for compliance

**Negative:**
- JWT tokens do not automatically refresh when roles change -- users must re-login to pick up new roles
- SQLite is single-writer; high concurrency on portal.db could be a bottleneck if the team grows significantly
- Module-level enforcement is client-side only (sidebar) -- a user who navigates directly to a restricted URL will reach the page. Middleware only enforces department-level. This is acceptable for Phase 2 (internal team, low attack surface).

---

## Migration

On first portal.db creation, the schema is bootstrapped automatically via `db-portal.ts::bootstrapPortalSchema`. No manual migration needed.

On EC2 deployment, ensure `portal.db` path is set correctly:
```
PORTAL_DB_PATH=/home/ubuntu/ananas-ai/portal.db
```
