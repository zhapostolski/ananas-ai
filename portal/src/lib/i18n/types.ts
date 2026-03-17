export type Language = "en" | "sr" | "mk";

export interface Translations {
  // Nav groups
  nav_marketing: string;
  nav_finance: string;
  nav_logistics: string;
  nav_executive: string;
  nav_customer_experience: string;
  nav_hr: string;
  nav_admin: string;
  nav_ai_chat: string;
  nav_settings: string;
  nav_profile: string;

  // Nav children — Marketing
  nav_overview: string;
  nav_performance: string;
  nav_crm: string;
  nav_reputation: string;
  nav_influencers: string;
  nav_marketing_ops: string;

  // Nav children — Customer Experience
  nav_reputation_reviews: string;
  nav_support_insights: string;

  // Nav children — HR
  nav_team: string;
  nav_attendance: string;

  // Nav children — Admin
  nav_users: string;
  nav_invite_user: string;
  nav_send_notification: string;

  // Breadcrumbs (page titles)
  page_overview: string;
  page_performance: string;
  page_crm: string;
  page_reputation: string;
  page_influencers: string;
  page_marketing_ops: string;
  page_finance: string;
  page_logistics: string;
  page_executive: string;
  page_customer_experience: string;
  page_reputation_reviews: string;
  page_support_insights: string;
  page_profile: string;
  page_settings: string;
  page_user_management: string;
  page_invite_user: string;
  page_send_notification: string;
  page_hr: string;
  page_team: string;
  page_attendance: string;

  // Common labels
  last_run: string;
  last_updated: string;
  loading: string;
  no_data: string;
  agent_analysis: string;
  channel_breakdown: string;
  live_ga4: string;
  target: string;
  phase_2: string;
  critical: string;
  good: string;
  on_target: string;
  below_target: string;

  // Overview page
  overview_subtitle: string;
  overview_sessions_7d: string;
  overview_revenue_7d: string;
  overview_blended_roas: string;
  overview_google_business: string;
  overview_daily_summary: string;
  overview_agent_status: string;
  overview_no_summary: string;

  // Performance page
  performance_subtitle: string;
  performance_ga4_section: string;
  performance_paid_section: string;
  performance_revenue: string;
  performance_sessions: string;
  performance_users: string;
  performance_conversion_rate: string;
  performance_total_spend: string;
  performance_blended_roas: string;
  performance_poas: string;
  performance_poas_desc: string;
  performance_all_channels: string;
  performance_all_paid: string;
  performance_no_channel_data: string;
  performance_loading_channels: string;

  // CRM page
  crm_subtitle: string;
  crm_alert_no_automations: string;
  crm_alert_no_automations_detail: string;
  crm_cart_section: string;
  crm_email_section: string;
  crm_retention_section: string;
  crm_cart_abandonment: string;
  crm_cart_recovery: string;
  crm_aov: string;
  crm_email_open_rate: string;
  crm_revenue_per_send: string;
  crm_active_subscribers: string;
  crm_churn_rate: string;
  crm_repeat_purchase: string;
  crm_ltv_cac: string;
  crm_new_vs_returning: string;
  crm_no_automation_badge: string;
  crm_target_35: string;
  crm_target_15: string;
  crm_no_recovery: string;
  crm_subscribers_desc: string;
  crm_retention_target: string;
  crm_repeat_target: string;

  // Reputation page
  ops_subtitle: string;
  ops_tracking_status: string;
  ops_ga4_sessions: string;
  ops_sc_clicks: string;
  ops_sc_impressions: string;
  ops_ga4_pipeline: string;
  ops_live_signal: string;
  ops_last_7d: string;
  ops_active_alerts: string;
  ops_notes: string;
  ops_full_report: string;
  ops_ok: string;
  ops_warning: string;

  rep_subtitle: string;
  rep_critical_trustpilot: string;
  rep_critical_unclaimed: string;
  rep_trustpilot_section: string;
  rep_google_section: string;
  rep_action_plan: string;
  rep_rating: string;
  rep_reviews: string;
  rep_response_rate: string;
  rep_profile_status: string;
  rep_claimed: string;
  rep_unclaimed: string;
  rep_total_reviews: string;
  rep_unanswered: string;
  rep_gbp_status: string;
  rep_priority_actions: string;
  rep_action_claim_tp: string;
  rep_action_respond: string;
  rep_action_review_email: string;
  rep_action_claim_gbp: string;
  rep_action_weekly_review: string;
  rep_target_45: string;
  rep_target_80: string;
  rep_tp_rating_desc: string;
  rep_gbp_rating_desc: string;
  rep_critical_trustpilot_detail: string;
  rep_critical_unclaimed_detail: string;
  rep_respond_sla: string;
  rep_not_configured: string;
  action_required: string;

  // Theme toggle
  toggle_theme: string;

  // Language switcher
  language: string;
  lang_en: string;
  lang_sr: string;
  lang_mk: string;

  // Sign out
  sign_out: string;
  my_profile: string;
  admin_panel: string;

  // Agent names
  agent_performance: string;
  agent_crm: string;
  agent_reputation: string;
  agent_ops: string;
  agent_brief: string;

  // Translating indicator
  translating: string;
}
