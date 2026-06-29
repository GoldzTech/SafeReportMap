import React, { useEffect, useMemo, useState } from 'react';
import {
  AlertTriangle,
  BarChart3,
  ChevronDown,
  Download,
  Filter,
  MapPin,
  ShieldAlert,
  Sparkles,
  TrendingUp,
  Users,
  X,
  RefreshCw,
  CheckCircle2,
  Send,
  Loader2,
  LogOut,
} from 'lucide-react';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import {
  exportReports,
  getAdminDashboardMetrics,
  getAdminReports,
  getAdminReportDetail,
  getAnalyticsDashboard,
  getHeatmapPoints,
  getStoredAccessToken,
} from './lib/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
const statusStyleMap = {
  RECEIVED: 'bg-sky-500/15 text-sky-200 ring-1 ring-sky-500/30',
  IN_REVIEW: 'bg-amber-500/15 text-amber-200 ring-1 ring-amber-500/30',
  FORWARDED: 'bg-violet-500/15 text-violet-200 ring-1 ring-violet-500/30',
  RESOLVED: 'bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-500/30',
};

const severityStyleMap = {
  LOW: 'bg-emerald-500/15 text-emerald-200 ring-1 ring-emerald-500/30',
  MEDIUM: 'bg-amber-500/15 text-amber-200 ring-1 ring-amber-500/30',
  HIGH: 'bg-orange-500/15 text-orange-200 ring-1 ring-orange-500/30',
  CRITICAL: 'bg-rose-500/15 text-rose-200 ring-1 ring-rose-500/30',
};

const statusLabelMap = {
  RECEIVED: 'Recebidos',
  IN_REVIEW: 'Em revisão',
  FORWARDED: 'Encaminhados',
  RESOLVED: 'Resolvidos',
};

function formatPriority(value) {
  if (value === null || value === undefined) return '-';
  return Number(value).toFixed(2);
}

function formatDateTime(value) {
  if (!value) return '-';
  try {
    return new Intl.DateTimeFormat('pt-BR', {
      dateStyle: 'short',
      timeStyle: 'short',
    }).format(new Date(value));
  } catch {
    return String(value);
  }
}

function MiniMetric({ label, value, delta, accent }) {
  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl">
      <div className={`mb-5 h-1.5 rounded-full bg-gradient-to-r ${accent}`} />
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{label}</p>
          <div className="mt-2 text-3xl font-semibold text-white">{value}</div>
        </div>
        {delta ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 px-3 py-1.5 text-xs font-medium text-emerald-300">
            {delta}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function DetailRow({ label, value }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-slate-950/50 p-4">
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
      <div className="mt-2 text-sm leading-6 text-slate-200">{value ?? '-'}</div>
    </div>
  );
}

async function postJson(path, body) {
  const token = getStoredAccessToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

async function patchJson(path, body) {
  const token = getStoredAccessToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  const text = await response.text();
  return text ? JSON.parse(text) : {};
}

export default function SafeReportAdminDashboard({ onLogout }) {
  const [query, setQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [actionMessage, setActionMessage] = useState('');
  const [actionError, setActionError] = useState('');
  const [actionLoading, setActionLoading] = useState('');
  const [dashboard, setDashboard] = useState({
    metrics: null,
    analytics: null,
    reports: [],
    heatmap: [],
  });
  const [selectedReport, setSelectedReport] = useState(null);
  const [selectedReportDetail, setSelectedReportDetail] = useState(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const loadDashboard = async (signal) => {
    setLoading(true);
    setError('');
    try {
      const params = {
        page: 1,
        pageSize: 8,
        status: statusFilter === 'ALL' ? undefined : statusFilter,
        search: query.trim() || undefined,
      };

      const [metrics, analytics, reports, heatmap] = await Promise.all([
        getAdminDashboardMetrics({ signal }),
        getAnalyticsDashboard({ signal }),
        getAdminReports(params, { signal }),
        getHeatmapPoints({ signal }),
      ]);

      setDashboard({
        metrics,
        analytics,
        reports: reports?.items ?? [],
        heatmap: heatmap?.points ?? [],
      });
    } catch (err) {
      if (err?.name !== 'AbortError') {
        setError('Não foi possível carregar o painel. Verifique o backend e a URL da API.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const controller = new AbortController();
    const timer = setTimeout(() => {
      loadDashboard(controller.signal);
    }, 250);

    return () => {
      controller.abort();
      clearTimeout(timer);
    };
  }, [query, statusFilter]);

  const cards = useMemo(() => {
    const metrics = dashboard.metrics;
    const analytics = dashboard.analytics?.overview;

    return [
      {
        label: 'Relatos',
        value: metrics?.total_reports ?? analytics?.total_reports ?? 0,
        delta: null,
        accent: 'from-sky-500 to-cyan-400',
      },
      {
        label: 'Em revisão',
        value: metrics?.reports_in_review ?? analytics?.reports_in_review ?? 0,
        delta: null,
        accent: 'from-amber-500 to-orange-400',
      },
      {
        label: 'Críticos',
        value: metrics?.critical_reports ?? analytics?.critical_reports ?? 0,
        delta: null,
        accent: 'from-rose-500 to-red-500',
      },
      {
        label: 'Clusters ativos',
        value: metrics?.active_clusters ?? analytics?.active_clusters ?? 0,
        delta: null,
        accent: 'from-violet-500 to-fuchsia-500',
      },
    ];
  }, [dashboard.metrics, dashboard.analytics]);

  const timeline = dashboard.analytics?.timeline ?? [];
  const categories = dashboard.analytics?.categories ?? [];
  const severities = dashboard.analytics?.severities ?? [];
  const topLocations = dashboard.analytics?.top_locations ?? [];
  const clusters = dashboard.analytics?.clusters ?? [];

  const refreshAfterAction = async (reportId) => {
    await loadDashboard();
    if (selectedReport?.id === reportId) {
      try {
        const detail = await getAdminReportDetail(reportId);
        setSelectedReportDetail(detail);
      } catch {
        setSelectedReportDetail((prev) => prev);
      }
    }
  };

  const handleOpenCase = async (report) => {
    setSelectedReport(report);
    setSelectedReportDetail(null);
    setActionMessage('');
    setActionError('');
    setDetailLoading(true);

    try {
      const detail = await getAdminReportDetail(report.id);
      setSelectedReportDetail(detail);
    } catch {
      setSelectedReportDetail(report);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleCloseCase = () => {
    setSelectedReport(null);
    setSelectedReportDetail(null);
    setDetailLoading(false);
    setActionMessage('');
    setActionError('');
    setActionLoading('');
  };

  const handleTriggerTriagem = async () => {
    if (!selectedReport) return;
    setActionLoading('triage');
    setActionMessage('');
    setActionError('');

    try {
      await postJson(`/api/v1/internal/triage/${selectedReport.id}`, {});
      setActionMessage('Triagem acionada com sucesso.');
      await refreshAfterAction(selectedReport.id);
    } catch (err) {
      setActionError(err?.message || 'Falha ao acionar triagem.');
    } finally {
      setActionLoading('');
    }
  };

  const handleSetStatus = async (newStatus) => {
    if (!selectedReport) return;
    if (!DEMO_ADMIN_ID) {
      setActionError('Defina VITE_DEMO_ADMIN_ID no .env.local para mudar status no painel.');
      return;
    }

    setActionLoading(newStatus);
    setActionMessage('');
    setActionError('');

    try {
      await patchJson(`/api/v1/admin/reports/${selectedReport.id}/status`, {
        changed_by: DEMO_ADMIN_ID,
        new_status: newStatus,
        reason: newStatus === 'RESOLVED' ? 'Caso concluído pelo painel administrativo.' : 'Encaminhamento pelo painel administrativo.',
      });
      setActionMessage(newStatus === 'RESOLVED' ? 'Caso marcado como concluído.' : 'Caso encaminhado com sucesso.');
      await refreshAfterAction(selectedReport.id);
    } catch (err) {
      setActionError(err?.message || 'Falha ao atualizar status.');
    } finally {
      setActionLoading('');
    }
  };

  const handleExportCsv = async () => {
    try {
      const blob = await exportReports({
        format: 'csv',
        status: statusFilter === 'ALL' ? undefined : statusFilter,
        search: query.trim() || undefined,
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'safereport_map_export.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    } catch {
      setError('Falha ao gerar a exportação CSV.');
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 opacity-40">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-0 top-24 h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto flex max-w-[1600px] gap-6 p-4 lg:p-6">
        <aside className="hidden w-72 shrink-0 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:block">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-400 to-violet-500 text-slate-950 shadow-lg shadow-cyan-500/20">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <div className="text-sm font-semibold text-white">SafeReport Map</div>
              <div className="text-xs text-slate-400">Área Interna</div>
            </div>
          </div>

          <nav className="space-y-2 text-sm">
            {['Dashboard', 'Relatos', 'Mapa', 'Analytics', 'Clusters', 'Exportações', 'Auditoria'].map((item, index) => (
              <button
                key={item}
                className={`flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left transition ${
                  index === 0 ? 'bg-white/10 text-white' : 'text-slate-300 hover:bg-white/5 hover:text-white'
                }`}
              >
                <span>{item}</span>
                <ChevronDown className="h-4 w-4 opacity-40" />
              </button>
            ))}
            <button
              onClick={onLogout}
              className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/10"
            >
              <LogOut className="h-4 w-4" />
              Sair
            </button>
          </nav>

          <div className="mt-8 rounded-3xl border border-white/10 bg-gradient-to-br from-cyan-500/10 to-fuchsia-500/10 p-4">
            <div className="flex items-center gap-2 text-sm font-medium text-white">
              <Sparkles className="h-4 w-4 text-cyan-300" />
              IA active
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Triagem automática, priorização e detecção de recorrência com fallback seguro.
            </p>
          </div>
        </aside>

        <main className="min-w-0 flex-1 space-y-6">
          <header className="rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-xl sm:p-5 lg:p-6">
            <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
              <div>
                <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-200">
                  <TrendingUp className="h-3.5 w-3.5" />
                  Painel Interno
                </div>
                <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">
                  SafeReport Map • Área Interna
                </h1>
                <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-400 sm:text-base">
                  Visualize relatos, priorização por IA, recorrência institucional e exportações anonimizadas em uma interface clara e responsiva.
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                <div className="flex items-center gap-2 rounded-2xl border border-white/10 bg-slate-900/70 px-3 py-2 text-sm text-slate-300">
                  <Filter className="h-4 w-4" />
                  <select className="bg-transparent outline-none" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
                    <option className="bg-slate-900" value="ALL">Todos os status</option>
                    <option className="bg-slate-900" value="RECEIVED">Recebidos</option>
                    <option className="bg-slate-900" value="IN_REVIEW">Em revisão</option>
                    <option className="bg-slate-900" value="FORWARDED">Encaminhados</option>
                    <option className="bg-slate-900" value="RESOLVED">Resolvidos</option>
                  </select>
                </div>

                <button onClick={handleExportCsv} className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-white/10">
                  <Download className="h-4 w-4" />
                  Exportar CSV
                </button>
              </div>
            </div>

            <div className="mt-5 grid gap-3 sm:grid-cols-[1fr_auto]">
              <div className="rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-400">
                <span className="text-slate-500">Busca:</span>{' '}
                <input
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Procure por código, local, categoria..."
                  className="w-full bg-transparent text-slate-100 outline-none placeholder:text-slate-600 sm:inline sm:w-auto"
                />
              </div>
              <div className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm text-slate-300 sm:min-w-72">
                <div className="flex items-center gap-2">
                  <MapPin className="h-4 w-4 text-cyan-300" />
                  Corrente institucional
                </div>
                <div className="font-medium text-white">Bloco A • Bloco B • Pátio</div>
              </div>
            </div>
          </header>

          {error ? (
            <div className="rounded-3xl border border-rose-500/20 bg-rose-500/10 p-4 text-sm text-rose-100">
              {error}
            </div>
          ) : null}

          <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {cards.map((item) => (
              <MiniMetric key={item.label} {...item} />
            ))}
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.4fr_0.9fr]">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-white">Volume e triagem ao longo do período</h2>
                  <p className="text-sm text-slate-400">Relatos recebidos x relatados em análise</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-slate-950/60 px-3 py-2 text-xs text-slate-300">
                  analytics / dashboard
                </div>
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={timeline}>
                    <defs>
                      <linearGradient id="reportsGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#22d3ee" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#22d3ee" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="triagedGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#a855f7" stopOpacity={0.35} />
                        <stop offset="95%" stopColor="#a855f7" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip
                      contentStyle={{
                        background: 'rgba(2, 6, 23, 0.98)',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: 16,
                        color: '#fff',
                      }}
                    />
                    <Legend />
                    <Area type="monotone" dataKey="count" stroke="#22d3ee" fill="url(#reportsGradient)" name="Recebidos" />
                    <Area type="monotone" dataKey="triaged" stroke="#a855f7" fill="url(#triagedGradient)" name="Triados" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-white">Severidade</h2>
                  <p className="text-sm text-slate-400">Distribuição atual dos casos</p>
                </div>
                <ShieldAlert className="h-5 w-5 text-rose-300" />
              </div>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={severities} layout="vertical">
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                    <XAxis type="number" stroke="#94a3b8" />
                    <YAxis type="category" dataKey="severity" stroke="#94a3b8" width={90} />
                    <Tooltip
                      contentStyle={{
                        background: 'rgba(2, 6, 23, 0.98)',
                        border: '1px solid rgba(255,255,255,0.08)',
                        borderRadius: 16,
                        color: '#fff',
                      }}
                    />
                    <Bar dataKey="count" radius={[0, 12, 12, 0]}>
                      {severities.map((entry, index) => (
                        <Cell key={`severity-${entry.severity}-${index}`} fill={['#10b981', '#f59e0b', '#f97316', '#ef4444'][index] ?? '#22d3ee'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </section>

          <section className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <h2 className="text-lg font-semibold text-white">Casos recentes</h2>
                  <p className="text-sm text-slate-400">Lista operacional para triagem humana</p>
                </div>
                <Users className="h-5 w-5 text-cyan-300" />
              </div>

              {loading ? (
                <div className="rounded-3xl border border-white/10 bg-slate-950/60 p-6 text-sm text-slate-400">
                  Carregando casos...
                </div>
              ) : (
                <div className="space-y-3">
                  {dashboard.reports.map((report) => (
                    <article key={report.id ?? report.public_reference_code} className="rounded-3xl border border-white/10 bg-slate-950/60 p-4 transition hover:border-white/20 hover:bg-slate-950/80">
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                        <div className="min-w-0">
                          <div className="flex flex-wrap items-center gap-2">
                            <span className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1 text-xs font-medium text-slate-300">
                              {report.public_reference_code}
                            </span>
                            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${severityStyleMap[report.ai_severity] ?? severityStyleMap.MEDIUM}`}>
                              {report.ai_severity ?? 'MEDIUM'}
                            </span>
                            <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusStyleMap[report.status] ?? statusStyleMap.RECEIVED}`}>
                              {statusLabelMap[report.status] ?? report.status}
                            </span>
                          </div>
                          <h3 className="mt-3 truncate text-base font-semibold text-white">
                            {report.ai_category ?? 'Sem categoria'}
                          </h3>
                          <p className="mt-1 text-sm leading-6 text-slate-400">
                            {report.ai_summary ?? report.content_sanitized ?? 'Sem resumo disponível.'}
                          </p>
                          <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-400">
                            <span>{report.location_text}</span>
                            <span>•</span>
                            <span>{report.location_zone ?? 'Sem zona'}</span>
                            <span>•</span>
                            <span>{formatDateTime(report.created_at)}</span>
                          </div>
                        </div>

                        <div className="flex shrink-0 items-center gap-3 lg:flex-col lg:items-end">
                          <div className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-right">
                            <p className="text-xs text-slate-400">Priority</p>
                            <p className="text-xl font-semibold text-white">{formatPriority(report.ai_priority_score ?? report.priority_score)}</p>
                          </div>
                          <button
                            onClick={() => handleOpenCase(report)}
                            className="rounded-2xl bg-white px-4 py-2 text-sm font-medium text-slate-950 transition hover:bg-cyan-100"
                          >
                            Abrir caso
                          </button>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}
            </div>

            <div className="space-y-4">
              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-white">Mapa de recorrência</h2>
                    <p className="text-sm text-slate-400">Heatmap simplificado por local</p>
                  </div>
                  <MapPin className="h-5 w-5 text-emerald-300" />
                </div>
                <div className="space-y-3">
                  {dashboard.heatmap.length === 0 ? (
                    <div className="rounded-2xl border border-white/10 bg-slate-950/60 p-4 text-sm text-slate-400">
                      Sem pontos de mapa ainda.
                    </div>
                  ) : (
                    dashboard.heatmap.map((point) => (
                      <div key={point.report_id}>
                        <div className="mb-1 flex items-center justify-between text-sm">
                          <span className="text-slate-300">{point.location_zone ?? 'Sem zona'}</span>
                          <span className="text-slate-400">{Math.round((point.intensity ?? 0) * 100)}%</span>
                        </div>
                        <div className="h-3 rounded-full bg-white/10">
                          <div
                            className="h-3 rounded-full bg-gradient-to-r from-cyan-400 via-violet-500 to-rose-500"
                            style={{ width: `${Math.min(Math.max((point.intensity ?? 0) * 100, 8), 100)}%` }}
                          />
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-white">Categorias</h2>
                    <p className="text-sm text-slate-400">Distribuição dos relatos</p>
                  </div>
                  <BarChart3 className="h-5 w-5 text-fuchsia-300" />
                </div>
                <div className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={categories}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.08)" />
                      <XAxis dataKey="category" stroke="#94a3b8" interval={0} angle={-20} textAnchor="end" height={60} />
                      <YAxis stroke="#94a3b8" />
                      <Tooltip
                        contentStyle={{
                          background: 'rgba(2, 6, 23, 0.98)',
                          border: '1px solid rgba(255,255,255,0.08)',
                          borderRadius: 16,
                          color: '#fff',
                        }}
                      />
                      <Bar dataKey="count" radius={[12, 12, 0, 0]} fill="#22d3ee" />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-white">Top localizações</h2>
                    <p className="text-sm text-slate-400">Baseada em analytics</p>
                  </div>
                  <AlertTriangle className="h-5 w-5 text-amber-300" />
                </div>
                <div className="space-y-3">
                  {(topLocations ?? []).slice(0, 5).map((item) => (
                    <div key={item.location_zone ?? 'none'} className="flex items-center justify-between rounded-2xl border border-white/10 bg-slate-950/60 px-4 py-3 text-sm">
                      <span className="text-slate-300">{item.location_zone ?? 'Sem zona'}</span>
                      <span className="font-medium text-white">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl lg:p-6">
                <div className="mb-4 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-white">Clusters</h2>
                    <p className="text-sm text-slate-400">Recorrência e agrupamentos</p>
                  </div>
                  <Sparkles className="h-5 w-5 text-cyan-300" />
                </div>
                <div className="space-y-3">
                  {(clusters ?? []).slice(0, 4).map((cluster) => (
                    <div key={cluster.cluster_id} className="rounded-2xl border border-white/10 bg-slate-950/60 p-4">
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <p className="font-medium text-white">{cluster.label}</p>
                          <p className="mt-1 text-xs uppercase tracking-wide text-slate-500">{cluster.cluster_type}</p>
                        </div>
                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${severityStyleMap[cluster.severity_level] ?? severityStyleMap.MEDIUM}`}>
                          {cluster.severity_level ?? 'MEDIUM'}
                        </span>
                      </div>
                      <div className="mt-3 text-sm text-slate-400">Recorrências: {cluster.recurrence_count}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>

      {selectedReport ? (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-slate-950/70 px-4 py-6 backdrop-blur-sm sm:items-center">
          <div className="max-h-[92vh] w-full max-w-4xl overflow-hidden rounded-3xl border border-white/10 bg-slate-950 shadow-2xl shadow-black/40 flex flex-col">
            <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
              <div>
                <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Detalhe do caso</p>
                <h3 className="mt-1 text-lg font-semibold text-white">{selectedReport.public_reference_code}</h3>
              </div>
              <button
                onClick={handleCloseCase}
                className="inline-flex items-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-3 py-2 text-sm text-white transition hover:bg-white/10"
              >
                <X className="h-4 w-4" />
                Fechar
              </button>
            </div>

            <div className="grid min-h-0 flex-1 gap-0 overflow-y-auto lg:grid-cols-[1.2fr_0.8fr]">
              <div className="space-y-4 overflow-y-auto p-5">
                {detailLoading ? (
                  <div className="rounded-3xl border border-white/10 bg-white/5 p-6 text-sm text-slate-400">
                    Carregando detalhes...
                  </div>
                ) : (
                  <>
                    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                      <div className="flex flex-wrap gap-2">
                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${severityStyleMap[selectedReportDetail?.ai_severity ?? selectedReport.ai_severity] ?? severityStyleMap.MEDIUM}`}>
                          {selectedReportDetail?.ai_severity ?? selectedReport.ai_severity ?? 'MEDIUM'}
                        </span>
                        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusStyleMap[selectedReportDetail?.status ?? selectedReport.status] ?? statusStyleMap.RECEIVED}`}>
                          {statusLabelMap[selectedReportDetail?.status ?? selectedReport.status] ?? selectedReport.status}
                        </span>
                      </div>
                      <h4 className="mt-4 text-xl font-semibold text-white">
                        {selectedReportDetail?.ai_category ?? selectedReport.ai_category ?? 'Sem categoria'}
                      </h4>
                      <p className="mt-3 text-sm leading-7 text-slate-300">
                        {selectedReportDetail?.ai_summary ?? selectedReport.ai_summary ?? 'Sem resumo disponível.'}
                      </p>
                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <DetailRow
                          label="Priority"
                          value={formatPriority(selectedReportDetail?.ai_priority_score ?? selectedReport.ai_priority_score)}
                        />
                        <DetailRow
                          label="Confidence"
                          value={selectedReportDetail?.ai_confidence ?? selectedReport.ai_confidence ?? '-'}
                        />
                      </div>
                    </div>

                    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                      <h5 className="text-sm font-semibold text-white">Conteúdo sanitizado</h5>
                      <p className="mt-3 whitespace-pre-wrap text-sm leading-7 text-slate-300">
                        {selectedReportDetail?.content_sanitized ?? selectedReport.content_sanitized ?? 'Sem conteúdo disponível.'}
                      </p>
                    </div>

                    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
                      <h5 className="text-sm font-semibold text-white">Justificativa IA</h5>
                      <p className="mt-3 text-sm leading-7 text-slate-300">
                        {selectedReportDetail?.ai_justification ?? 'Sem justificativa disponível.'}
                      </p>
                    </div>
                  </>
                )}
              </div>

              <div className="space-y-4 border-t border-white/10 bg-slate-950/40 p-5 lg:border-l lg:border-t-0">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <h5 className="text-sm font-semibold text-white">Ações rápidas</h5>
                  <div className="mt-4 grid gap-2">
                    <button
                      type="button"
                      onClick={handleTriggerTriagem}
                      disabled={actionLoading === 'triage'}
                      className="inline-flex items-center justify-center gap-2 rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {actionLoading === 'triage' ? <Loader2 className="h-4 w-4 animate-spin" /> : <RefreshCw className="h-4 w-4" />}
                      Triar agora
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSetStatus('FORWARDED')}
                      disabled={actionLoading === 'FORWARDED'}
                      className="inline-flex items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm font-semibold text-white transition hover:bg-white/10 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {actionLoading === 'FORWARDED' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
                      Encaminhar
                    </button>
                    <button
                      type="button"
                      onClick={() => handleSetStatus('RESOLVED')}
                      disabled={actionLoading === 'RESOLVED'}
                      className="inline-flex items-center justify-center gap-2 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm font-semibold text-emerald-100 transition hover:bg-emerald-500/20 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      {actionLoading === 'RESOLVED' ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
                      Concluir caso
                    </button>
                  </div>
                  {actionMessage ? (
                    <div className="mt-3 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 px-4 py-3 text-sm text-emerald-100">
                      {actionMessage}
                    </div>
                  ) : null}
                  {actionError ? (
                    <div className="mt-3 rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                      {actionError}
                    </div>
                  ) : null}
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <h5 className="text-sm font-semibold text-white">Metadados</h5>
                  <div className="mt-3 space-y-2 text-sm text-slate-300">
                    <div><span className="text-slate-500">Local:</span> {selectedReportDetail?.location_text ?? selectedReport.location_text}</div>
                    <div><span className="text-slate-500">Zona:</span> {selectedReportDetail?.location_zone ?? selectedReport.location_zone ?? 'Sem zona'}</div>
                    <div><span className="text-slate-500">Criado em:</span> {formatDateTime(selectedReportDetail?.created_at ?? selectedReport.created_at)}</div>
                    <div><span className="text-slate-500">Incidente em:</span> {selectedReportDetail?.incident_date ?? selectedReport.incident_date ?? '-'}</div>
                    <div><span className="text-slate-500">Urgência:</span> {selectedReportDetail?.urgency_self_reported ?? '-'}</div>
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <h5 className="text-sm font-semibold text-white">Keywords</h5>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {(selectedReportDetail?.keywords ?? []).length > 0 ? (
                      (selectedReportDetail?.keywords ?? []).map((kw) => (
                        <span key={kw} className="rounded-full bg-cyan-400/10 px-3 py-1 text-xs text-cyan-200 ring-1 ring-cyan-400/20">
                          {kw}
                        </span>
                      ))
                    ) : (
                      <span className="text-sm text-slate-500">Sem keywords disponíveis.</span>
                    )}
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <h5 className="text-sm font-semibold text-white">Status atual</h5>
                  <div className="mt-3 text-sm text-slate-300">
                    {selectedReportDetail?.status ?? selectedReport.status}
                  </div>
                </div>

                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <h5 className="text-sm font-semibold text-white">Resumo operacional</h5>
                  <p className="mt-3 text-sm leading-6 text-slate-300">
                    Esse caso pode ser usado na demo para mostrar leitura rápida, priorização por IA e decisão humana sobre o fluxo.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

