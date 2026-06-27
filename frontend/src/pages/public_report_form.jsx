import React, { useMemo, useState } from 'react';
import { Paperclip, Send, ShieldCheck, Sparkles } from 'lucide-react';

const MAX_CHARS = 4000;

async function submitAnonymousReport(payload) {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, '') || 'http://127.0.0.1:8000';

  const response = await fetch(`${baseUrl}/api/v1/reports`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const detail = await response.text().catch(() => '');
    throw new Error(detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

function FieldLabel({ children, hint }) {
  return (
    <div className="mb-2 flex items-end justify-between gap-3">
      <label className="text-sm font-medium text-slate-200">{children}</label>
      {hint ? <span className="text-xs text-slate-500">{hint}</span> : null}
    </div>
  );
}

function InputShell({ children, className = '' }) {
  return (
    <div className={`rounded-2xl border border-white/10 bg-slate-950/70 px-4 py-3 text-slate-100 shadow-inner shadow-black/20 ${className}`}>
      {children}
    </div>
  );
}

export default function PublicReportForm() {
  const [form, setForm] = useState({
    incident_date: '',
    location_text: '',
    location_zone: '',
    content_raw: '',
    urgency_self_reported: 3,
    attachments: [],
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(null);

  const remainingChars = useMemo(() => MAX_CHARS - form.content_raw.length, [form.content_raw]);

  const setField = (key, value) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const handleFileChange = (event) => {
    const files = Array.from(event.target.files || []);
    setField('attachments', files);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(null);

    try {
      if (!form.content_raw.trim()) {
        throw new Error('Descreva o ocorrido antes de enviar.');
      }

      const payload = {
        incident_date: form.incident_date || null,
        location_text: form.location_text.trim(),
        location_zone: form.location_zone.trim() || null,
        content_raw: form.content_raw.trim(),
        urgency_self_reported: Number(form.urgency_self_reported),
        attachments: [],
      };

      const result = await submitAnonymousReport(payload);
      setSuccess(result);
      setForm({
        incident_date: '',
        location_text: '',
        location_zone: '',
        content_raw: '',
        urgency_self_reported: 3,
        attachments: [],
      });
    } catch (err) {
      setError(err?.message || 'Não foi possível enviar o relato.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="pointer-events-none fixed inset-0 opacity-40">
        <div className="absolute left-0 top-0 h-72 w-72 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="absolute right-0 top-24 h-80 w-80 rounded-full bg-fuchsia-500/20 blur-3xl" />
        <div className="absolute bottom-0 left-1/3 h-80 w-80 rounded-full bg-emerald-500/10 blur-3xl" />
      </div>

      <div className="relative mx-auto max-w-6xl px-4 py-6 sm:px-6 lg:px-8">
        <header className="mb-6 flex items-center justify-between gap-4 rounded-3xl border border-white/10 bg-white/5 px-5 py-4 backdrop-blur-xl">
          <div>
            <div className="mb-2 inline-flex items-center gap-2 rounded-full border border-cyan-400/20 bg-cyan-400/10 px-3 py-1 text-xs font-medium text-cyan-200">
              <ShieldCheck className="h-3.5 w-3.5" />
              Relato anônimo
            </div>
            <h1 className="text-2xl font-semibold tracking-tight text-white sm:text-3xl">SafeReport Map</h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
              Preencha com o máximo de clareza possível. Não informe nomes, telefones ou dados desnecessários.
            </p>
          </div>
        </header>

        <div className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
          <form onSubmit={handleSubmit} className="space-y-6 rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl sm:p-6 lg:p-8">
            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <FieldLabel hint="Opcional">Data aproximada</FieldLabel>
                <InputShell>
                  <input
                    type="date"
                    value={form.incident_date}
                    onChange={(e) => setField('incident_date', e.target.value)}
                    className="w-full bg-transparent outline-none placeholder:text-slate-600"
                  />
                </InputShell>
              </div>

              <div>
                <FieldLabel hint="Ex.: corredor, sala, banheiro">Local</FieldLabel>
                <InputShell>
                  <input
                    value={form.location_text}
                    onChange={(e) => setField('location_text', e.target.value)}
                    placeholder="Ex.: Corredor central"
                    className="w-full bg-transparent outline-none placeholder:text-slate-600"
                  />
                </InputShell>
              </div>

              <div>
                <FieldLabel hint="Opcional">Zona / setor</FieldLabel>
                <InputShell>
                  <input
                    value={form.location_zone}
                    onChange={(e) => setField('location_zone', e.target.value)}
                    placeholder="Ex.: Bloco A"
                    className="w-full bg-transparent outline-none placeholder:text-slate-600"
                  />
                </InputShell>
              </div>

              <div>
                <FieldLabel hint="1 = baixa, 5 = urgente">Urgência percebida</FieldLabel>
                <InputShell>
                  <select
                    value={form.urgency_self_reported}
                    onChange={(e) => setField('urgency_self_reported', Number(e.target.value))}
                    className="w-full bg-transparent outline-none"
                  >
                    <option className="bg-slate-900" value={1}>1 - Baixa</option>
                    <option className="bg-slate-900" value={2}>2 - Leve</option>
                    <option className="bg-slate-900" value={3}>3 - Média</option>
                    <option className="bg-slate-900" value={4}>4 - Alta</option>
                    <option className="bg-slate-900" value={5}>5 - Urgente</option>
                  </select>
                </InputShell>
              </div>
            </div>

            <div>
              <FieldLabel hint={`${remainingChars} caracteres restantes`}>Descreva o ocorrido</FieldLabel>
              <InputShell className="px-0 py-0">
                <textarea
                  value={form.content_raw}
                  onChange={(e) => setField('content_raw', e.target.value.slice(0, MAX_CHARS))}
                  placeholder="Conte o que aconteceu com detalhes objetivos."
                  rows={9}
                  className="min-h-[220px] w-full resize-none rounded-2xl bg-transparent px-4 py-3 outline-none placeholder:text-slate-600"
                />
              </InputShell>
              <div className="mt-2 flex items-center justify-between text-xs text-slate-500">
                <span>Evite nomes próprios, telefones e dados que possam identificar alguém.</span>
                <span>{form.content_raw.length}/{MAX_CHARS}</span>
              </div>
            </div>

            <div>
              <FieldLabel hint="Opcional">Anexo simples</FieldLabel>
              <InputShell>
                <label className="flex cursor-pointer items-center gap-3 text-sm text-slate-300">
                  <Paperclip className="h-4 w-4 text-cyan-300" />
                  <span>{form.attachments?.length ? `${form.attachments.length} arquivo(s) selecionado(s)` : 'Clique para escolher arquivos'}</span>
                  <input
                    type="file"
                    className="hidden"
                    onChange={handleFileChange}
                    multiple
                    accept="image/*,application/pdf"
                  />
                </label>
              </InputShell>
              <p className="mt-2 text-xs leading-6 text-slate-500">
                sem upload real ainda; campo pronto, mas sem a funcionalidade.
              </p>
            </div>

            {error ? (
              <div className="rounded-3xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-sm text-rose-100">
                {error}
              </div>
            ) : null}

            <button
              type="submit"
              disabled={loading}
              className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-white px-4 py-3.5 text-sm font-semibold text-slate-950 transition hover:bg-cyan-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Enviando...' : 'Enviar relato anônimo'}
              <Send className="h-4 w-4" />
            </button>
          </form>

          <aside className="space-y-6">
            <div className="rounded-3xl border border-white/10 bg-white/5 p-5 backdrop-blur-xl sm:p-6">
              <div className="flex items-center gap-2 text-sm font-medium text-white">
                <Sparkles className="h-4 w-4 text-cyan-300" />
                Como o relato será tratado
              </div>
              <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
                <li>1. O relato é salvo de forma segura.</li>
                <li>2. A IA faz triagem e priorização.</li>
                <li>3. O painel administrativo recebe o caso.</li>
                <li>4. O gestor toma a decisão final.</li>
              </ul>
            </div>

            <div className="rounded-3xl border border-white/10 bg-gradient-to-br from-cyan-500/10 to-fuchsia-500/10 p-5 backdrop-blur-xl sm:p-6">
              <h2 className="text-lg font-semibold text-white">Boas práticas</h2>
              <div className="mt-4 space-y-3 text-sm leading-6 text-slate-300">
                <p>• Escreva com objetividade.</p>
                <p>• Inclua local e data aproximada sempre que possível.</p>
                <p>• Não inclua nomes, e-mails, telefones ou documentos.</p>
                <p>• Se houve recorrência, diga isso explicitamente.</p>
              </div>
            </div>

            {success ? (
              <div className="rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-5 text-sm text-emerald-100">
                <div className="font-semibold">Relato enviado com sucesso</div>
                <p className="mt-2 leading-6">
                  Código de confirmação: <span className="font-mono">{success.public_reference_code}</span>
                </p>
                <p className="mt-1 leading-6">Status inicial: {success.status}</p>
                <p className="mt-1 leading-6">{success.message}</p>
              </div>
            ) : null}
          </aside>
        </div>
      </div>
    </div>
  );
}
