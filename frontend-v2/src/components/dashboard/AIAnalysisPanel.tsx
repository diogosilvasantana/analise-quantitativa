import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Brain } from 'lucide-react';
import { AIAnalysisData } from '@/types/dashboard';

interface AIAnalysisPanelProps {
    data?: AIAnalysisData;
}

// --- Sub-Component: Asset Context Card (WIN/WDO) ---
interface AIContextCardProps {
    title: string;
    assetType: 'WIN' | 'WDO';
    context?: {
        bias: string;
        magnets: string[];
        structure: string;
        alert: string;
    };
}

export function AIContextCard({ title, assetType, context }: AIContextCardProps) {
    const isWin = assetType === 'WIN';
    const titleColor = isWin ? 'text-blue-400' : 'text-green-400';
    const badgeBorder = isWin ? 'border-blue-900 text-blue-300' : 'border-green-900 text-green-300';
    const magnetBg = isWin ? 'bg-blue-900/20 text-blue-300' : 'bg-green-900/20 text-green-300';

    return (
        <Card className="bg-slate-900 border-slate-800 h-full">
            <CardHeader className="pb-2 pt-3">
                <div className="flex justify-between items-center">
                    <CardTitle className={`text-sm font-bold ${titleColor}`}>{title}</CardTitle>
                    <Badge variant="outline" className={badgeBorder}>{context?.bias || 'N/A'}</Badge>
                </div>
            </CardHeader>
            <CardContent className="space-y-3 text-sm pt-0">
                {context ? (
                    <>
                        <div>
                            <span className="text-slate-500 text-xs uppercase block">Estrutura</span>
                            <span className="text-slate-300">{context.structure || 'Aguardando...'}</span>
                        </div>
                        <div>
                            <span className="text-slate-500 text-xs uppercase block">Ímãs (Objetivos)</span>
                            <div className="flex flex-wrap gap-1 mt-1">
                                {context.magnets?.map((m, i) => (
                                    <span key={i} className={`${magnetBg} px-2 py-0.5 rounded text-xs`}>{m}</span>
                                )) || <span className="text-slate-500 text-xs">Sem alvos definidos</span>}
                            </div>
                        </div>
                        <div className="bg-yellow-900/10 border border-yellow-900/30 p-2 rounded">
                            <div className="flex items-center gap-2 text-yellow-500 text-xs font-bold mb-1">
                                <AlertTriangle className="w-3 h-3" /> ALERTA
                            </div>
                            <p className="text-xs text-yellow-200/80">{context.alert || 'Nenhum alerta crítico.'}</p>
                        </div>
                    </>
                ) : (
                    <div className="text-slate-500 text-sm">Dados de contexto indisponíveis.</div>
                )}
            </CardContent>
        </Card>
    );
}

// --- Main Component: Global Narrative (Sidebar) ---
export function AIAnalysisPanel({ data: propData }: AIAnalysisPanelProps) {
    const [data, setData] = useState<AIAnalysisData | null>(propData || null);
    const [loading, setLoading] = useState(!propData);

    useEffect(() => {
        if (propData) {
            setData(propData);
            setLoading(false);
        }
    }, [propData]);

    useEffect(() => {
        if (propData) return;
        const fetchAnalysis = async () => {
            try {
                const response = await fetch('http://localhost:8000/api/analysis/latest');
                const result = await response.json();
                if (!result.error) setData(result);
            } catch (error) {
                console.error("Failed to fetch AI analysis:", error);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalysis();
        const interval = setInterval(fetchAnalysis, 300000);
        return () => clearInterval(interval);
    }, [propData]);

    if (loading) return <div className="p-4 text-center text-slate-500">Carregando análise...</div>;
    if (!data) return null;

    return (
        <Card className="w-full bg-slate-900/50 border-slate-800 text-slate-100 backdrop-blur-sm h-full">
            <CardHeader className="pb-2">
                <CardTitle className="text-lg font-bold flex items-center gap-2 text-purple-400">
                    <Brain className="w-5 h-5" />
                    Jarvis Global
                </CardTitle>
                <div className="text-xs text-slate-500">
                    Atualizado às <span className="text-slate-300 font-mono">{data.timestamp || '--:--'}</span>
                </div>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Narrative */}
                <div className="bg-slate-950/50 p-3 rounded-lg border border-slate-800">
                    <h4 className="text-xs font-bold text-slate-400 mb-1 uppercase">Narrativa do Dia</h4>
                    <p className="text-slate-200 text-xs leading-relaxed italic border-l-2 border-purple-500 pl-2">
                        "{data.narrative}"
                    </p>
                </div>

                {/* Players Outlook */}
                <div className="space-y-2">
                    <h4 className="text-xs font-bold text-slate-400 uppercase">Visão dos Players</h4>
                    <div className="grid grid-cols-1 gap-2">
                        <div className="bg-slate-900/40 p-2 rounded border border-slate-800 flex justify-between items-center">
                            <span className="text-xs text-slate-400">Estrangeiros</span>
                            <span className="text-xs text-slate-300 font-medium">{data.players_outlook?.foreigners || 'N/A'}</span>
                        </div>
                        <div className="bg-slate-900/40 p-2 rounded border border-slate-800 flex justify-between items-center">
                            <span className="text-xs text-slate-400">Institucionais</span>
                            <span className="text-xs text-slate-300 font-medium">{data.players_outlook?.institutions || 'N/A'}</span>
                        </div>
                        <div className="bg-slate-900/40 p-2 rounded border border-slate-800 flex justify-between items-center">
                            <span className="text-xs text-slate-400">Varejo (Risco)</span>
                            <span className="text-xs text-slate-300 font-medium">{data.players_outlook?.retail_risk || 'N/A'}</span>
                        </div>
                    </div>
                </div>

                {/* Executive Summary */}
                <div className="bg-purple-900/20 border border-purple-900/50 p-2 rounded text-center">
                    <span className="text-purple-300 font-medium text-xs">"{data.executive_summary || 'Analisando...'}"</span>
                </div>
            </CardContent>
        </Card>
    );
}