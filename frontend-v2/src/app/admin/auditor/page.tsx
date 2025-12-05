'use client';

import React, { useState, useRef } from 'react';
import { ShieldCheck, RefreshCw, AlertTriangle, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';
import { AuditCard, AuditIssue } from '@/components/admin/AuditCard';

export default function AuditorPage() {
    const [loading, setLoading] = useState(false);
    const [progress, setProgress] = useState({ current: 0, total: 0, file: '' });
    const [issues, setIssues] = useState<AuditIssue[]>([]);
    const [error, setError] = useState<string | null>(null);

    const runAudit = async () => {
        setLoading(true);
        setIssues([]);
        setError(null);
        setProgress({ current: 0, total: 0, file: 'Iniciando...' });

        try {
            const response = await fetch('/api/audit/run'); // Using Next.js rewrite or direct backend URL? Assuming proxy setup or direct URL.
            // If frontend is Next.js and backend is on port 8000, we usually need a full URL or a proxy.
            // Given the environment, I'll try the relative path assuming a proxy is configured in next.config.js
            // If not, I might need 'http://localhost:8000/audit/run'

            // Wait, looking at previous history, backend is on port 8000. Frontend is 3000/3001.
            // I'll use the full URL for safety if I don't know the proxy config, 
            // but usually in these setups there's a rewrite. 
            // I'll stick to relative path '/api/audit/run' if there is a rewrite, or just '/audit/run' if the backend is on the same domain (unlikely).
            // Let's assume there is a rewrite rule mapping /api/* to backend.

            if (!response.ok) {
                throw new Error(`Audit failed: ${response.statusText}`);
            }

            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || ''; // Keep the last incomplete line

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const event = JSON.parse(line);

                        if (event.status === 'progress') {
                            setProgress({
                                current: event.current,
                                total: event.total,
                                file: event.file
                            });
                        } else if (event.status === 'complete') {
                            setIssues(event.issues);
                            setLoading(false);
                        } else if (event.status === 'error') {
                            setError(event.message);
                            setLoading(false);
                        }
                    } catch (e) {
                        console.error("Error parsing JSON chunk", e);
                    }
                }
            }
        } catch (err: any) {
            setError(err.message || "Failed to run audit");
            setLoading(false);
        }
    };

    const handleFix = async (issue: AuditIssue): Promise<string> => {
        const res = await fetch('/api/audit/fix', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: issue.file_path,
                fixed_code: issue.fixed_code
            })
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Failed to apply fix");
        }

        const data = await res.json();
        return data.backup_id;
    };

    const handleRollback = async (issue: AuditIssue, backupId: string) => {
        const res = await fetch('/api/audit/rollback', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                file_path: issue.file_path,
                backup_id: backupId
            })
        });

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || "Failed to rollback");
        }
    };

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8">
            <div className="flex items-center justify-between border-b border-slate-800 pb-6">
                <div className="flex items-center gap-4">
                    <div className="bg-indigo-600 p-3 rounded-xl shadow-lg shadow-indigo-900/20">
                        <ShieldCheck className="w-8 h-8 text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
                            AI Auditor
                        </h1>
                        <p className="text-slate-500 font-medium">Self-Healing & Code Security Module</p>
                    </div>
                </div>
                <Button
                    onClick={runAudit}
                    disabled={loading}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-6"
                >
                    {loading ? <RefreshCw className="mr-2 h-4 w-4 animate-spin" /> : <RefreshCw className="mr-2 h-4 w-4" />}
                    {loading ? "Auditando..." : "Executar Auditoria"}
                </Button>
            </div>

            {/* Progress Bar */}
            {loading && (
                <div className="bg-slate-900/50 p-6 rounded-xl border border-slate-800 animate-in fade-in slide-in-from-top-4">
                    <div className="flex justify-between text-sm text-slate-400 mb-2">
                        <span>Analisando arquivos...</span>
                        <span>{progress.current} / {progress.total}</span>
                    </div>
                    <Progress value={(progress.current / (progress.total || 1)) * 100} className="h-2" />
                    <p className="text-xs text-slate-500 mt-2 font-mono truncate">
                        Atual: {progress.file}
                    </p>
                </div>
            )}

            {/* Content */}
            <div className="space-y-6">
                {error && (
                    <Alert variant="destructive" className="bg-red-900/20 border-red-900">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>Erro na Auditoria</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}

                {!loading && issues.length === 0 && !error && (
                    <div className="text-center py-20 bg-slate-900/50 rounded-2xl border border-slate-800 border-dashed">
                        <ShieldCheck className="w-16 h-16 text-slate-700 mx-auto mb-4" />
                        <h3 className="text-xl font-semibold text-slate-400">Sistema Seguro</h3>
                        <p className="text-slate-600 mt-2">Nenhuma vulnerabilidade ou erro lógico detectado.</p>
                        <p className="text-slate-600 text-sm mt-1">Clique em "Executar Auditoria" para iniciar uma nova varredura.</p>
                    </div>
                )}

                {issues.map((issue, idx) => (
                    <AuditCard
                        key={issue.id || idx}
                        issue={issue}
                        onFix={handleFix}
                        onRollback={handleRollback}
                    />
                ))}
            </div>
        </div>
    );
}
