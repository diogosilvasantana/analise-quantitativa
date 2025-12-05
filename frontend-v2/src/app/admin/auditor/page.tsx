'use client';

import React, { useState } from 'react';
import { AuditCard } from '@/components/admin/AuditCard';
import { Button } from "@/components/ui/button";
import { ShieldCheck, RefreshCw, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

// API Helpers (Move to a service later)
const API_URL = "http://localhost:8000"; // Adjust if needed

export default function AuditorPage() {
    const [issues, setIssues] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const runAudit = async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_URL}/audit/run`);
            if (!res.ok) throw new Error("Failed to fetch audit results");
            const data = await res.json();
            if (Array.isArray(data)) {
                setIssues(data);
            } else {
                throw new Error(data.detail || data.message || "Invalid response format");
            }
        } catch (e: any) {
            setError(e.message);
        } finally {
            setLoading(false);
        }
    };

    const handleFix = async (issue: any) => {
        const res = await fetch(`${API_URL}/audit/fix`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: issue.file_path, fixed_code: issue.fixed_code })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Fix failed");
        }
        const data = await res.json();
        return data.backup_id;
    };

    const handleRollback = async (issue: any, backupId: string) => {
        const res = await fetch(`${API_URL}/audit/rollback`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ file_path: issue.file_path, backup_id: backupId })
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Rollback failed");
        }
    };

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-8 font-sans">
            <div className="max-w-4xl mx-auto space-y-8">

                {/* Header */}
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
                        {loading ? "Analisando..." : "Executar Auditoria"}
                    </Button>
                </div>

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
        </div>
    );
}
