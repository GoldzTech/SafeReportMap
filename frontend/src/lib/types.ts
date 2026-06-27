export type ReportStatus = 'RECEIVED' | 'IN_REVIEW' | 'FORWARDED' | 'RESOLVED';

export type SeverityLevel = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type IncidentCategory =
  | 'VERBAL_HARASSMENT'
  | 'DISCRIMINATION'
  | 'INTIMIDATION'
  | 'EXCLUSION'
  | 'THREAT'
  | 'INAPPROPRIATE_PHYSICAL_CONTACT'
  | 'OTHER';

export interface DashboardMetrics {
  total_reports: number;
  reports_in_review: number;
  critical_reports: number;
  high_reports: number;
  active_clusters: number;
  recurrence_rate: number;
  most_common_category: IncidentCategory | null;
  most_common_severity: SeverityLevel | null;
}

export interface TimelinePoint {
  day: string;
  count: number;
  triaged?: number;
}

export interface CategoryStat {
  category: string;
  count: number;
}

export interface SeverityStat {
  severity: SeverityLevel | string;
  count: number;
}

export interface LocationStat {
  location_zone: string | null;
  count: number;
}

export interface ClusterStat {
  cluster_id: string;
  label: string;
  cluster_type: string;
  recurrence_count: number;
  severity_level: SeverityLevel | null;
}

export interface AnalyticsDashboardResponse {
  overview: DashboardMetrics;
  timeline: TimelinePoint[];
  categories: CategoryStat[];
  severities: SeverityStat[];
  top_locations: LocationStat[];
  clusters: ClusterStat[];
}

export interface AdminReportListItem {
  id: string;
  public_reference_code: string;
  incident_date: string | null;
  location_text: string;
  location_zone: string | null;
  status: ReportStatus;
  created_at: string;
  ai_category: string | null;
  ai_severity: SeverityLevel | null;
  ai_priority_score: number | null;
  ai_summary: string | null;
  ai_confidence: number | null;
  recurrence_flag: boolean;
  cluster_id: string | null;
  content_sanitized?: string;
  priority_score?: number | null;
}

export interface AdminReportPage {
  items: AdminReportListItem[];
  meta: {
    page: number;
    page_size: number;
    total: number;
    total_pages: number;
  };
}

export interface HeatmapPoint {
  report_id: string;
  location_zone: string | null;
  cluster_id: string | null;
  severity: SeverityLevel | string | null;
  intensity: number;
}

export interface HeatmapResponse {
  points: HeatmapPoint[];
}

export interface AdminReportDetail extends AdminReportListItem {
  content_raw: string;
  content_sanitized: string;
  urgency_self_reported: number | null;
  submitted_from_demo: boolean;
  is_deleted: boolean;
  updated_at: string;
  ai_justification: string | null;
  model_version: string | null;
  processed_at: string | null;
  recurrence_score: number | null;
  keywords: string[];
  notes: Array<{
    id: string;
    report_id: string;
    admin_id: string;
    content: string;
    is_private: boolean;
    created_at: string;
    updated_at: string;
  }>;
  status_history: Array<{
    id: string;
    report_id: string;
    previous_status: string | null;
    new_status: string;
    changed_by: string | null;
    reason: string | null;
    changed_at: string;
  }>;
  attachments: Array<{
    id: string;
    report_id: string;
    file_name: string;
    file_path: string;
    mime_type: string;
    file_size_bytes: number;
    created_at: string;
    is_deleted: boolean;
  }>;
}