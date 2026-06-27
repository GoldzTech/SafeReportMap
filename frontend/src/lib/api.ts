import type {
  AdminReportPage,
  AnalyticsDashboardResponse,
  DashboardMetrics,
  HeatmapResponse,
  ReportStatus,
  SeverityLevel,
  IncidentCategory,
  AdminReportDetail,
} from './types';

// import.meta.env typing can vary between environments; cast to any to safely read values
const _meta: any = import.meta;
const rawBaseUrl = _meta?.env?.local?.VITE_API_BASE_URL ?? _meta?.env?.VITE_API_BASE_URL;
const API_BASE_URL = rawBaseUrl?.replace(/\/$/, '') || 'http://127.0.0.1:8000';

const AUTH_SESSION_KEY = 'safereport_auth_session';

export interface AuthSession {
  access_token: string;
  token_type: string;
  role: string;
  user_id: string;
  tenant_id: string;
}

type RequestOptions = {
  signal?: AbortSignal;
  auth?: boolean;
  method?: string;
  body?: BodyInit | null;
  headers?: HeadersInit;
};

function buildQuery(params: Record<string, string | number | undefined | null>) {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

function readStoredSession(): AuthSession | null {
  if (typeof window === 'undefined') return null;

  const raw = window.localStorage.getItem(AUTH_SESSION_KEY);
  if (!raw) return null;

  try {
    return JSON.parse(raw) as AuthSession;
  } catch {
    return null;
  }
}

export function getStoredAuthSession(): AuthSession | null {
  return readStoredSession();
}

export function setStoredAuthSession(session: AuthSession): void {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(AUTH_SESSION_KEY, JSON.stringify(session));
}

export function clearStoredAuthSession(): void {
  if (typeof window === 'undefined') return;
  window.localStorage.removeItem(AUTH_SESSION_KEY);
}

export function getStoredAccessToken(): string | null {
  return readStoredSession()?.access_token ?? null;
}

function buildHeaders(headers?: HeadersInit, includeAuth = true): Headers {
  const finalHeaders = new Headers(headers ?? {});

  if (!finalHeaders.has('Accept')) {
    finalHeaders.set('Accept', 'application/json');
  }

  if (includeAuth) {
    const token = getStoredAccessToken();
    if (token && !finalHeaders.has('Authorization')) {
      finalHeaders.set('Authorization', `Bearer ${token}`);
    }
  }

  return finalHeaders;
}

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers: buildHeaders(options.headers, options.auth !== false),
    signal: options.signal,
    body: options.body,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  const text = await response.text();
  if (!text) return {} as T;

  return JSON.parse(text) as T;
}

async function requestBlob(path: string, options: RequestOptions = {}): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: options.method ?? 'GET',
    headers: buildHeaders(options.headers, options.auth !== false),
    signal: options.signal,
    body: options.body,
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.blob();
}

export async function loginAdmin(payload: { email: string; password: string }): Promise<AuthSession> {
  return requestJson<AuthSession>('/api/v1/auth/login', {
    method: 'POST',
    auth: false,
    body: JSON.stringify(payload),
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
  });
}

export async function getAdminDashboardMetrics(options: RequestOptions = {}) {
  return requestJson<DashboardMetrics>('/api/v1/admin/dashboard/metrics', options);
}

export async function getAnalyticsDashboard(options: RequestOptions = {}) {
  return requestJson<AnalyticsDashboardResponse>('/api/v1/analytics/dashboard', options);
}

export async function getAdminReports(
  params: {
    page?: number;
    pageSize?: number;
    status?: ReportStatus;
    severity?: SeverityLevel;
    category?: IncidentCategory;
    zone?: string;
    search?: string;
  } = {},
  options: RequestOptions = {},
) {
  const query = buildQuery({
    page: params.page ?? 1,
    page_size: params.pageSize ?? 8,
    status: params.status,
    severity: params.severity,
    category: params.category,
    zone: params.zone,
    search: params.search,
  });

  return requestJson<AdminReportPage>(`/api/v1/admin/reports${query}`, options);
}

export async function getHeatmapPoints(options: RequestOptions = {}) {
  return requestJson<HeatmapResponse>('/api/v1/map/heatmap', options);
}

export async function exportReports(params: {
  format: 'csv' | 'pdf';
  status?: ReportStatus;
  severity?: SeverityLevel;
  category?: IncidentCategory;
  zone?: string;
  search?: string;
}): Promise<Blob> {
  const query = buildQuery({
    format: params.format,
    status: params.status,
    severity: params.severity,
    category: params.category,
    zone: params.zone,
    search: params.search,
  });

  return requestBlob(`/api/v1/admin/export${query}`, {
    headers: {
      Accept: params.format === 'pdf' ? 'application/pdf' : 'text/csv',
    },
  });
}

export async function getAdminReportDetail(reportId: string, options: RequestOptions = {}) {
  return requestJson<AdminReportDetail>(`/api/v1/admin/reports/${reportId}`, options);
}