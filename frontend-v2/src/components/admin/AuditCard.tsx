import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, CheckCircle, RotateCcw, Play, Loader2, FileCode } from 'lucide-react';
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";

interface AuditIssue {
    id: string;
    file_path: string;
    category?: "LOGIC" | "SECURITY" | "UX" | "VISUAL" | "OPTIMIZATION";
    severity: "CRITICAL" | "WARNING" | "INFO";
    title: string;
    description: string;
    original_code: string;
    fixed_code: string;
}

interface AuditCardProps {
    issue: AuditIssue;
    onFix: (issue: AuditIssue) => Promise<string>; // Returns backup_id
    onRollback: (issue: AuditIssue, backupId: string) => Promise<void>;
}

export const AuditCard: React.FC<AuditCardProps> = ({ issue, onFix, onRollback }) => {
    const [status, setStatus] = useState<"pending" | "fixing" | "fixed" | "rolling_back">("pending");
    const [backupId, setBackupId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleFix = async () => {
        setStatus("fixing");
        setError(null);
        try {
            const bid = await onFix(issue);
            setBackupId(bid);
            setStatus("fixed");
        } catch (e: any) {
            setError(e.message || "Failed to fix");
            setStatus("pending");
        }
    };

    const handleRollback = async () => {
        if (!backupId) return;
        setStatus("rolling_back");
        setError(null);
        try {
            await onRollback(issue, backupId);
            setStatus("pending");
            setBackupId(null);
        } catch (e: any) {
            setError(e.message || "Failed to rollback");
            setStatus("fixed"); // Stay in fixed state if rollback fails
        }
    };

    const getSeverityColor = (s: string) => {
        switch (s) {
            case "CRITICAL": return "bg-red-500/20 text-red-500 border-red-500/50";
            case "WARNING": return "bg-yellow-500/20 text-yellow-500 border-yellow-500/50";
            default: return "bg-blue-500/20 text-blue-500 border-blue-500/50";
        }
    };

    const getCategoryColor = (c?: string) => {
        switch (c) {
            case "LOGIC": return "bg-purple-500/20 text-purple-400 border-purple-500/50";
            case "SECURITY": return "bg-red-500/20 text-red-500 border-red-500/50";
            case "UX": return "bg-pink-500/20 text-pink-400 border-pink-500/50";
            case "VISUAL": return "bg-cyan-500/20 text-cyan-400 border-cyan-500/50";
            case "OPTIMIZATION": return "bg-emerald-500/20 text-emerald-400 border-emerald-500/50";
            default: return "bg-slate-500/20 text-slate-400 border-slate-500/50";
        }
    };

    return (
        <Card className="bg-slate-900 border-slate-800 mb-4 overflow-hidden">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div className="space-y-1">
                        <div className="flex items-center gap-2">
                            {issue.category && (
                                <Badge variant="outline" className={`${getCategoryColor(issue.category)}`}>
                                    {issue.category}
                                </Badge>
                            )}
                            <Badge variant="outline" className={`${getSeverityColor(issue.severity)}`}>
                                {issue.severity}
                            </Badge>
                            <span className="text-slate-400 text-xs flex items-center gap-1">
                                <FileCode className="w-3 h-3" />
                                {issue.file_path}
                            </span>
                        </div>
                        <CardTitle className="text-lg text-slate-200">{issue.title}</CardTitle>
                    </div>
                </div>
                <CardDescription className="text-slate-400 mt-2">
                    {issue.description}
                </CardDescription>
            </CardHeader>

            <CardContent className="py-4">
                {/* Simple Diff View (Visual only for now) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs font-mono">
                    <div className="bg-red-950/30 p-3 rounded border border-red-900/30 overflow-auto max-h-60">
                        <p className="text-red-400 mb-2 font-bold sticky top-0 bg-red-950/90 p-1">ORIGINAL</p>
                        <pre className="whitespace-pre-wrap text-red-200/70">{(issue.original_code || "").substring(0, 500)}...</pre>
                    </div>
                    <div className="bg-green-950/30 p-3 rounded border border-green-900/30 overflow-auto max-h-60">
                        <p className="text-green-400 mb-2 font-bold sticky top-0 bg-green-950/90 p-1">CORRIGIDO (PREVIEW)</p>
                        <pre className="whitespace-pre-wrap text-green-200/70">{(issue.fixed_code || "").substring(0, 500)}...</pre>
                    </div>
                </div>

                {error && (
                    <Alert variant="destructive" className="mt-4 bg-red-900/20 border-red-900">
                        <AlertTriangle className="h-4 w-4" />
                        <AlertTitle>Erro</AlertTitle>
                        <AlertDescription>{error}</AlertDescription>
                    </Alert>
                )}
            </CardContent>

            <CardFooter className="bg-slate-950/50 border-t border-slate-800 pt-4 flex justify-end gap-3">
                {(status === "pending" || status === "fixing") && (
                    <Button onClick={handleFix} disabled={status === "fixing"} className="bg-blue-600 hover:bg-blue-700">
                        {status === "fixing" ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Play className="mr-2 h-4 w-4" />}
                        {status === "fixing" ? "Aplicando..." : "Aplicar Correção"}
                    </Button>
                )}

                {status === "fixed" && (
                    <div className="flex items-center gap-3 w-full justify-between">
                        <div className="flex items-center text-green-500 gap-2 text-sm font-medium">
                            <CheckCircle className="w-5 h-5" />
                            Correção Aplicada!
                        </div>
                        <Button onClick={handleRollback} variant="outline" className="border-slate-700 hover:bg-slate-800 text-slate-300">
                            <RotateCcw className="mr-2 h-4 w-4" />
                            Desfazer (Rollback)
                        </Button>
                    </div>
                )}

                {status === "rolling_back" && (
                    <Button disabled variant="outline" className="border-slate-700 text-slate-300">
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Restaurando...
                    </Button>
                )}
            </CardFooter>
        </Card>
    );
};
