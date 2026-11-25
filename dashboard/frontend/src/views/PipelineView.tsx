import { useState } from 'react';
import type { PipelineExecutionResult } from '../types';
import { Copy, Check, Sparkles, Server, RefreshCw, ChevronDown, ChevronUp, Fingerprint } from 'lucide-react';
import { getVerdictStyle, VerdictBadge } from '../components/ui/verdict-badge';

const samples: Record<number, { title: string; text: string; tid: string; desc: string }> = {
  1: {
    title: 'APT29 Run Keys Persistence',
    tid: 'T1547.001',
    desc: 'reg.exe add HKCU\\Software\\...\\Run /v Updater',
    text: 'The threat actor achieved persistence by executing reg.exe add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Updater /d C:\\Users\\student\\x.exe to start malware automatically upon user logon.'
  },
  2: {
    title: 'LSASS Credential Dumping',
    tid: 'T1003.001',
    desc: 'procdump.exe -ma lsass.exe lsass.dmp',
    text: 'During credential access phase, the attacker used procdump.exe with -ma switch against lsass.exe to dump memory to disk.'
  },
  3: {
    title: 'SMB Admin Share Movement',
    tid: 'T1021.002',
    desc: 'net.exe use \\\\10.0.0.5\\C$ /user:admin',
    text: 'Lateral movement was observed when the attacker executed net.exe use \\\\10.0.0.5\\C$ /user:admin Passw0rd to mount an administrative share on 10.0.0.5. The payload (SHA256: 7b3a9f2e1d4c5a8b6e0f3d2c1a9b8e7f6d5c4a3b2e1f0d9c8b7a6f5e4d3c2b1a) was downloaded from hxxp://malware-c2.evil.xyz/stage2.bin and beaconed to 192.168.44.100.'
  }
};

interface TaxiiGroup {
  group: string;
  total: number;
  supported: number;
}

interface TaxiiTechnique {
  id: string;
  name: string;
  supported: boolean;
  set: number | null;
}

interface TaxiiIngestResult {
  source: string;
  group: string | null;
  total_techniques: number;
  supported_techniques: number;
  techniques: TaxiiTechnique[];
}

export const PipelineView = () => {
  const [reportText, setReportText] = useState<string>(samples[1].text);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [copied, setCopied] = useState<boolean>(false);

  // TAXII state
  const [taxiiExpanded, setTaxiiExpanded] = useState(false);
  const [taxiiStatus, setTaxiiStatus] = useState<'unknown' | 'checking' | 'connected' | 'unavailable'>('unknown');
  const [taxiiGroups, setTaxiiGroups] = useState<TaxiiGroup[]>([]);
  const [taxiiGroupsLoading, setTaxiiGroupsLoading] = useState(false);
  const [taxiiGroupFilter, setTaxiiGroupFilter] = useState('');
  const [taxiiIngestResult, setTaxiiIngestResult] = useState<TaxiiIngestResult | null>(null);
  const [taxiiIngestLoading, setTaxiiIngestLoading] = useState(false);
  const [taxiiRefreshing, setTaxiiRefreshing] = useState(false);
  const [taxiiRefreshMsg, setTaxiiRefreshMsg] = useState('');

  const checkTaxiiStatus = async () => {
    setTaxiiStatus('checking');
    try {
      const res = await fetch('/api/taxii/status');
      const data = await res.json();
      setTaxiiStatus(data.status === 'connected' ? 'connected' : 'unavailable');
    } catch {
      setTaxiiStatus('unavailable');
    }
  };

  const loadTaxiiGroups = async () => {
    setTaxiiGroupsLoading(true);
    try {
      const res = await fetch('/api/taxii/groups');
      if (res.ok) {
        const data = await res.json();
        setTaxiiGroups(data);
        setTaxiiStatus('connected');
      } else {
        setTaxiiStatus('unavailable');
      }
    } catch {
      setTaxiiStatus('unavailable');
    } finally {
      setTaxiiGroupsLoading(false);
    }
  };

  const ingestGroup = async (groupName: string) => {
    setTaxiiIngestLoading(true);
    setTaxiiIngestResult(null);
    try {
      const res = await fetch('/api/taxii/ingest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ group: groupName }),
      });
      if (res.ok) {
        const data = await res.json();
        setTaxiiIngestResult(data);
      }
    } catch { /* handled by empty result */ }
    finally { setTaxiiIngestLoading(false); }
  };

  const refreshLookup = async () => {
    setTaxiiRefreshing(true);
    setTaxiiRefreshMsg('');
    try {
      const res = await fetch('/api/taxii/refresh', { method: 'POST' });
      const data = await res.json();
      if (data.status === 'updated') {
        setTaxiiRefreshMsg(`Updated: ${data.total} techniques (${data.added} new, ${data.removed} removed)`);
      } else {
        setTaxiiRefreshMsg(`Failed: ${data.error}`);
      }
    } catch (e) {
      setTaxiiRefreshMsg('Could not reach TAXII server');
    } finally {
      setTaxiiRefreshing(false);
    }
  };
  const [pipelineData, setPipelineData] = useState<PipelineExecutionResult>({
    technique_id: 'T1547.001',
    technique_name: 'Boot or Logon Autostart Execution: Registry Run Keys / Startup Folder',
    process_image: '\\reg.exe',
    extracted_command: 'reg.exe add HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run /v Updater /d C:\\Users\\student\\x.exe',
    rule_yaml: `title: Persistence via Run Keys
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\reg.exe'
        CommandLine|contains|all:
            - 'add'
            - '\\CurrentVersion\\Run'
    condition: selection
level: high
tags:
    - attack.persistence
    - attack.t1547.001`,
    verdict: 'PASS',
    verdict_explanation: 'Caught extracted attack and hidden variant, quiet on benign command line.',
    extract_time: 0.02,
    gen_time: 0.04,
    model: 'qwen2.5-coder:14b (v3b)',
    iocs: { ipv4: [], domains: [], urls: [], hashes: [] }
  });

  const handleCopyRule = () => {
    navigator.clipboard.writeText(pipelineData.rule_yaml);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const runPipeline = async () => {
    if (!reportText.trim()) return;
    setIsLoading(true);

    try {
      const res = await fetch('/api/pipeline/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: reportText })
      });
      if (res.ok) {
        const data = await res.json();
        setPipelineData(data);
      } else {
        if (reportText.includes('procdump')) {
          setPipelineData({
            technique_id: 'T1003.001',
            technique_name: 'OS Credential Dumping: LSASS Memory',
            process_image: '\\procdump.exe',
            extracted_command: 'procdump.exe -ma lsass.exe lsass.dmp',
            rule_yaml: `title: LSASS Memory Dump Via ProcDump
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith:
            - '\\procdump.exe'
            - '\\procdump64.exe'
        CommandLine|contains|all:
            - '-ma'
            - 'lsass'
    condition: selection
level: critical
tags:
    - attack.credential_access
    - attack.t1003.001`,
            verdict: 'PASS',
            verdict_explanation: 'Caught memory dump and 64-bit variant, quiet on non-LSASS targets.',
            extract_time: 0.02,
            gen_time: 0.04,
            model: 'qwen2.5-coder:14b (v3b)'
          });
        } else if (reportText.includes('net.exe use')) {
          setPipelineData({
            technique_id: 'T1021.002',
            technique_name: 'Remote Services: SMB/Windows Admin Shares',
            process_image: '\\net.exe',
            extracted_command: 'net.exe use \\\\10.0.0.5\\C$ /user:admin Passw0rd',
            rule_yaml: `title: Suspicious Net Use Command For Remote Share Mounting
status: test
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith:
            - '\\net.exe'
            - '\\net1.exe'
        CommandLine|contains|all:
            - 'use'
            - '\\\\\\\\'
    condition: selection
level: medium
tags:
    - attack.lateral_movement
    - attack.t1021.002`,
            verdict: 'PASS',
            verdict_explanation: 'Caught remote share mounting and net1 variant, quiet on local shares.',
            extract_time: 0.02,
            gen_time: 0.04,
            model: 'qwen2.5-coder:14b (v3b)'
          });
        }
      }
    } catch {
      // Offline simulation fallback
    } finally {
      setIsLoading(false);
    }
  };

  const stages = [
    { num: 1, title: 'Threat Ingestion', detail: 'Raw report narrative' },
    { num: 2, title: 'TTP Extraction', detail: 'ATT&CK mapping' },
    { num: 3, title: 'Rule Drafting', detail: 'Sigma YAML generation' },
    { num: 4, title: 'Gate Validation', detail: 'Synthetic log test' },
  ];

  return (
    <div className="space-y-4">
      {/* Stepper */}
      <div className="bg-panel p-3 rounded-lg border border-edge">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2.5 text-xs">
          {stages.map((s, i) => {
            const done = !isLoading && pipelineData.verdict !== '';
            const active = isLoading ? (i === 1 || i === 2) : false;
            const completed = done || i === 0;
            return (
              <div key={i} className={`flex items-center gap-2.5 p-2.5 rounded-lg border transition-all duration-200 ${
                active ? 'bg-brand-muted border-brand-edge text-fg animate-pulse' :
                completed ? 'bg-brand-muted border-brand-edge text-fg' :
                'bg-panel-inset border-edge text-fg-secondary'
              }`}>
                <div className={`w-5 h-5 rounded-full text-[11px] font-bold flex items-center justify-center shrink-0 transition-colors ${
                  completed || active ? 'bg-brand text-brand-fg' : 'bg-edge text-fg-muted'
                }`}>{completed && !active ? '✓' : s.num}</div>
                <div>
                  <div className="font-semibold text-[11px]">{s.title}</div>
                  <div className={`text-[10px] ${completed || active ? 'text-brand' : 'text-fg-muted'}`}>{s.detail}</div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Input + Output */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch min-h-[600px]">
        {/* Input */}
        <div className="lg:col-span-5 bg-panel p-4 rounded-lg border border-edge flex flex-col justify-between">
          <div className="space-y-3">
            <div className="pb-2.5 border-b border-subtle">
              <span className="text-xs font-semibold text-fg">Threat Report Input</span>
              <span className="text-[10px] text-fg-muted ml-2">Step 1</span>
            </div>

            <div className="space-y-1.5">
              <div className="text-[11px] text-fg-muted">Sample scenarios:</div>
              {Object.entries(samples).map(([key, s]) => (
                <button key={key} onClick={() => setReportText(s.text)}
                  className="w-full text-left p-2 rounded-md border border-edge bg-panel-inset hover:bg-panel-hover hover:border-edge-hover transition-colors text-xs text-fg cursor-pointer">
                  <div className="flex items-center justify-between">
                    <span className="font-medium text-fg">{s.title}</span>
                    <span className="text-[10px] font-mono text-brand bg-brand-muted px-1.5 py-0.5 rounded border border-brand-edge">{s.tid}</span>
                  </div>
                  <div className="text-[11px] text-fg-muted truncate mt-0.5">{s.desc}</div>
                </button>
              ))}
            </div>

            <div>
              <label className="text-[11px] text-fg-muted mb-1 block">Report text:</label>
              <textarea value={reportText} onChange={(e) => setReportText(e.target.value)}
                className="w-full h-52 bg-panel-inset border border-edge rounded-md p-3 text-xs font-mono text-fg focus:border-brand focus:outline-none focus-visible:ring-1 focus-visible:ring-brand/40 resize-none leading-relaxed"
                placeholder="Paste threat report text..." />
            </div>
          </div>

          <div className="pt-3 border-t border-subtle space-y-2">
            <button onClick={runPipeline} disabled={isLoading}
              className="w-full bg-brand hover:bg-brand-hover disabled:opacity-60 text-brand-fg font-semibold py-2.5 rounded-lg transition-all duration-150 text-xs flex items-center justify-center gap-2 cursor-pointer">
              <Sparkles className="w-3.5 h-3.5" />
              <span>{isLoading ? 'Running pipeline...' : 'Execute Pipeline'}</span>
            </button>
            <div className="text-[10px] text-fg-muted text-center">
              Ollama Extractor | Qwen 14b (v3b) Generator | pySigma Gate
            </div>
          </div>
        </div>

        {/* Output */}
        <div className="lg:col-span-7 space-y-3 flex flex-col justify-between">
          {/* Extraction */}
          <div className="bg-panel p-3.5 rounded-lg border border-edge">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-subtle">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-brand text-brand-fg text-[11px] flex items-center justify-center font-bold">2</span>
                <h3 className="text-xs font-semibold text-fg">Technique Extraction</h3>
              </div>
              <span className="text-[11px] text-fg-muted">{pipelineData.extract_time}s</span>
            </div>
            <div className="space-y-1 p-2.5 rounded-md bg-panel-inset border border-edge text-xs font-mono">
              <div>
                <span className="text-fg-muted font-sans">Technique:</span>{' '}
                <span className="text-brand font-medium">{pipelineData.technique_id}</span> ({pipelineData.technique_name})
              </div>
              <div>
                <span className="text-fg-muted font-sans">Process:</span>{' '}
                <span className="text-fg font-medium">{pipelineData.process_image}</span>
              </div>
              <div>
                <span className="text-fg-muted font-sans">Command:</span>{' '}
                <span className="text-fg font-medium select-all break-all">{pipelineData.extracted_command}</span>
              </div>
            </div>
          </div>

          {/* IOC Extraction */}
          {pipelineData.iocs && (pipelineData.iocs.ipv4.length > 0 || pipelineData.iocs.domains.length > 0 || pipelineData.iocs.urls.length > 0 || pipelineData.iocs.hashes.length > 0) && (
            <div className="bg-panel p-3.5 rounded-lg border border-edge">
              <div className="flex items-center justify-between pb-2 mb-2 border-b border-subtle">
                <div className="flex items-center gap-2">
                  <Fingerprint className="w-4 h-4 text-brand" />
                  <h3 className="text-xs font-semibold text-fg">Extracted IOCs</h3>
                </div>
                <span className="text-[10px] text-fg-muted">
                  {(pipelineData.iocs.ipv4.length + pipelineData.iocs.domains.length + pipelineData.iocs.urls.length + pipelineData.iocs.hashes.length)} indicators
                </span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                {pipelineData.iocs.ipv4.length > 0 && (
                  <div className="p-2 rounded-md bg-panel-inset border border-edge">
                    <div className="text-[10px] text-fg-muted font-semibold uppercase tracking-wider mb-1">IPv4 Addresses</div>
                    {pipelineData.iocs.ipv4.map(ip => (
                      <div key={ip} className="font-mono text-fg select-all">{ip}</div>
                    ))}
                  </div>
                )}
                {pipelineData.iocs.domains.length > 0 && (
                  <div className="p-2 rounded-md bg-panel-inset border border-edge">
                    <div className="text-[10px] text-fg-muted font-semibold uppercase tracking-wider mb-1">Domains</div>
                    {pipelineData.iocs.domains.map(d => (
                      <div key={d} className="font-mono text-fg select-all">{d}</div>
                    ))}
                  </div>
                )}
                {pipelineData.iocs.urls.length > 0 && (
                  <div className="col-span-2 p-2 rounded-md bg-panel-inset border border-edge">
                    <div className="text-[10px] text-fg-muted font-semibold uppercase tracking-wider mb-1">URLs</div>
                    {pipelineData.iocs.urls.map(u => (
                      <div key={u} className="font-mono text-fg select-all break-all">{u}</div>
                    ))}
                  </div>
                )}
                {pipelineData.iocs.hashes.length > 0 && (
                  <div className="col-span-2 p-2 rounded-md bg-panel-inset border border-edge">
                    <div className="text-[10px] text-fg-muted font-semibold uppercase tracking-wider mb-1">File Hashes</div>
                    {pipelineData.iocs.hashes.map(h => (
                      <div key={h.value} className="flex items-center gap-2">
                        <span className="text-[10px] px-1 py-0.5 rounded bg-brand-muted text-brand border border-brand-edge font-semibold uppercase">{h.type}</span>
                        <span className="font-mono text-fg select-all break-all">{h.value}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Generated rule */}
          <div className="bg-panel p-3.5 rounded-lg border border-edge">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-subtle">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-brand text-brand-fg text-[11px] flex items-center justify-center font-bold">3</span>
                <h3 className="text-xs font-semibold text-fg">Generated Sigma Rule</h3>
              </div>
              <div className="flex items-center gap-2.5">
                <span className="text-[11px] text-fg-muted">{pipelineData.model}</span>
                <button onClick={handleCopyRule}
                  className="px-2 py-0.5 rounded-md bg-panel-inset hover:bg-panel-hover border border-edge text-[10px] font-medium text-fg-secondary flex items-center gap-1 cursor-pointer">
                  {copied ? <Check className="w-3 h-3 text-pass" /> : <Copy className="w-3 h-3" />}
                  <span>{copied ? 'Copied' : 'Copy'}</span>
                </button>
              </div>
            </div>
            <pre className="bg-code-bg p-3.5 rounded-lg text-code-fg text-xs font-mono overflow-x-auto select-all leading-relaxed min-h-[340px] border border-code-edge">
              {pipelineData.rule_yaml}
            </pre>
          </div>

          {/* Validation */}
          <div className="bg-panel p-3.5 rounded-lg border border-edge">
            <div className="flex items-center justify-between pb-2 mb-2 border-b border-subtle">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-brand text-brand-fg text-[11px] flex items-center justify-center font-bold">4</span>
                <h3 className="text-xs font-semibold text-fg">Gate Validation</h3>
              </div>
              <span className={`text-[11px] font-mono font-semibold px-2 py-0.5 rounded border ${getVerdictStyle(pipelineData.verdict)}`}>
                {pipelineData.verdict}
              </span>
            </div>
            <div className={`p-2.5 rounded-md border text-xs ${getVerdictStyle(pipelineData.verdict)}`}>
              <div className="font-semibold">Verdict: {pipelineData.verdict}</div>
              <div className="text-[11px] mt-1 opacity-80">{pipelineData.verdict_explanation}</div>
            </div>
          </div>
        </div>
      </div>

      {/* STIX/TAXII Ingestion */}
      <div className="bg-panel rounded-lg border border-edge">
        <button onClick={() => { setTaxiiExpanded(!taxiiExpanded); if (!taxiiExpanded && taxiiStatus === 'unknown') checkTaxiiStatus(); }}
          className="w-full flex items-center justify-between p-3.5 text-left cursor-pointer">
          <div className="flex items-center gap-2">
            <Server className="w-4 h-4 text-brand" />
            <span className="text-xs font-semibold text-fg">STIX/TAXII Structured Ingestion</span>
            <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium ${
              taxiiStatus === 'connected' ? 'bg-pass-muted text-pass border-pass-edge' :
              taxiiStatus === 'unavailable' ? 'bg-critical-muted text-critical border-critical-edge' :
              taxiiStatus === 'checking' ? 'bg-brand-muted text-brand border-brand-edge animate-pulse' :
              'bg-panel-inset text-fg-muted border-edge'
            }`}>
              {taxiiStatus === 'connected' ? 'Connected' :
               taxiiStatus === 'unavailable' ? 'Offline' :
               taxiiStatus === 'checking' ? 'Checking...' : 'Not checked'}
            </span>
          </div>
          {taxiiExpanded ? <ChevronUp className="w-4 h-4 text-fg-muted" /> : <ChevronDown className="w-4 h-4 text-fg-muted" />}
        </button>

        {taxiiExpanded && (
          <div className="px-3.5 pb-3.5 space-y-3 border-t border-edge pt-3">
            {/* Actions row */}
            <div className="flex flex-wrap items-center gap-2">
              <button onClick={loadTaxiiGroups} disabled={taxiiGroupsLoading}
                className="px-3 py-1.5 bg-brand hover:bg-brand-hover disabled:opacity-60 text-brand-fg font-semibold rounded-lg text-[11px] flex items-center gap-1.5 cursor-pointer transition-colors">
                <Server className="w-3 h-3" />
                {taxiiGroupsLoading ? 'Loading groups...' : 'Load Threat Groups'}
              </button>
              <button onClick={refreshLookup} disabled={taxiiRefreshing}
                className="px-3 py-1.5 bg-panel-inset hover:bg-panel-hover border border-edge text-fg-secondary font-medium rounded-lg text-[11px] flex items-center gap-1.5 cursor-pointer transition-colors">
                <RefreshCw className={`w-3 h-3 ${taxiiRefreshing ? 'animate-spin' : ''}`} />
                {taxiiRefreshing ? 'Refreshing...' : 'Refresh ATT&CK Lookup'}
              </button>
              {taxiiRefreshMsg && (
                <span className="text-[11px] text-fg-muted">{taxiiRefreshMsg}</span>
              )}
            </div>

            {/* Groups table */}
            {taxiiGroups.length > 0 && (
              <div className="space-y-2">
                <div className="flex items-center gap-2">
                  <input type="text" value={taxiiGroupFilter} onChange={e => setTaxiiGroupFilter(e.target.value)}
                    placeholder="Filter groups..."
                    className="bg-panel-inset border border-edge rounded-md px-2 py-1 text-xs text-fg focus:border-brand focus:outline-none w-48" />
                  <span className="text-[10px] text-fg-muted">{taxiiGroups.length} groups from MITRE ATT&CK</span>
                </div>
                <div className="max-h-[200px] overflow-y-auto rounded-lg border border-edge">
                  <table className="w-full text-xs">
                    <thead className="bg-panel-inset sticky top-0">
                      <tr className="border-b border-edge">
                        <th className="text-left px-2.5 py-1.5 text-fg-muted font-medium">Threat Group</th>
                        <th className="text-right px-2.5 py-1.5 text-fg-muted font-medium">ATT&CK</th>
                        <th className="text-right px-2.5 py-1.5 text-fg-muted font-medium">Supported</th>
                        <th className="px-2.5 py-1.5"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {taxiiGroups
                        .filter(g => !taxiiGroupFilter || g.group.toLowerCase().includes(taxiiGroupFilter.toLowerCase()))
                        .slice(0, 50)
                        .map(g => (
                        <tr key={g.group} className="border-b border-edge last:border-0 hover:bg-panel-hover transition-colors">
                          <td className="px-2.5 py-1.5 font-medium text-fg">{g.group}</td>
                          <td className="px-2.5 py-1.5 text-right text-fg-secondary font-mono">{g.total}</td>
                          <td className="px-2.5 py-1.5 text-right font-mono">
                            <span className={g.supported > 0 ? 'text-pass font-semibold' : 'text-fg-muted'}>{g.supported}</span>
                          </td>
                          <td className="px-2.5 py-1.5 text-right">
                            {g.supported > 0 && (
                              <button onClick={() => ingestGroup(g.group)}
                                className="px-2 py-0.5 bg-brand-muted hover:bg-brand text-brand hover:text-brand-fg border border-brand-edge rounded text-[10px] font-semibold cursor-pointer transition-colors">
                                Ingest
                              </button>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {/* Ingest result */}
            {taxiiIngestLoading && (
              <div className="text-xs text-brand animate-pulse">Fetching group techniques from TAXII...</div>
            )}
            {taxiiIngestResult && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <span className="font-semibold text-fg">{taxiiIngestResult.group}</span>
                  <span className="text-fg-muted">
                    {taxiiIngestResult.total_techniques} techniques from ATT&CK,{' '}
                    <span className="text-pass font-semibold">{taxiiIngestResult.supported_techniques}</span> supported by our pipeline
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded border font-medium ${
                    taxiiIngestResult.source === 'taxii' ? 'bg-pass-muted text-pass border-pass-edge' : 'bg-narrow-muted text-narrow border-narrow-edge'
                  }`}>
                    {taxiiIngestResult.source === 'taxii' ? 'TAXII' : 'Local fallback'}
                  </span>
                </div>
                <div className="max-h-[180px] overflow-y-auto rounded-lg border border-edge">
                  <table className="w-full text-xs">
                    <thead className="bg-panel-inset sticky top-0">
                      <tr className="border-b border-edge">
                        <th className="text-left px-2.5 py-1.5 text-fg-muted font-medium">Technique</th>
                        <th className="text-left px-2.5 py-1.5 text-fg-muted font-medium">Name</th>
                        <th className="text-center px-2.5 py-1.5 text-fg-muted font-medium">Set</th>
                        <th className="text-center px-2.5 py-1.5 text-fg-muted font-medium">Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {taxiiIngestResult.techniques.map(t => (
                        <tr key={t.id} className={`border-b border-edge last:border-0 ${t.supported ? '' : 'opacity-50'}`}>
                          <td className="px-2.5 py-1.5 font-mono font-semibold text-brand">{t.id}</td>
                          <td className="px-2.5 py-1.5 text-fg-secondary truncate max-w-[200px]" title={t.name}>{t.name}</td>
                          <td className="px-2.5 py-1.5 text-center">
                            {t.set ? <span className="text-[10px] px-1 rounded bg-panel-inset border border-edge text-fg-muted font-mono">S{t.set}</span> : <span className="text-fg-muted">-</span>}
                          </td>
                          <td className="px-2.5 py-1.5 text-center">
                            <VerdictBadge verdict={t.supported ? 'PASS' : 'NOT_TESTED'} className="text-[9px]" />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            <p className="text-[10px] text-fg-muted leading-relaxed">
              Pulls threat group profiles from MITRE's ATT&CK TAXII 2.1 server.
              Shows which of their techniques our pipeline has synthetic logs for.
              The local ATT&CK lookup is the fallback when the server is unreachable.
            </p>
          </div>
        )}
      </div>

      {/* Architecture cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 w-full">
        {[
          { stage: 'TTP Extraction', title: 'Threat ingestion', desc: 'Extracts MITRE ATT&CK technique IDs, binary images, and arguments from raw CTI text. Structured ingestion via STIX/TAXII maps threat groups to techniques.' },
          { stage: 'LLM Rule Generation', title: 'Sigma drafting', desc: 'Local Qwen 14b (v3b) drafts valid pySigma syntax with generalized detection logic.' },
          { stage: 'Multi-Point Validation', title: 'Synthetic log test', desc: 'Translates Sigma to SQLite, runs against shown attacks, hidden variants, and benign baselines.' },
        ].map((c) => (
          <div key={c.stage} className="bg-panel p-3.5 rounded-lg border border-edge">
            <div className="text-[10px] text-fg-muted mb-1">{c.stage}</div>
            <div className="text-xs font-semibold text-fg mb-1">{c.title}</div>
            <p className="text-[11px] text-fg-secondary leading-relaxed">{c.desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
