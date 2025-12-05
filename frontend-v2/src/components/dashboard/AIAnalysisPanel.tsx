import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, Brain } from 'lucide-react';
import { AIAnalysisData } from '@/types/dashboard';

interface AIAnalysisPanelProps {
    data?: AIAnalysisData; // Now accepts data from parent (WebSocket)
}

export function AIAnalysisPanel({ data: propData }: AIAnalysisPanelProps) {
    const [data, setData] = useState<AIAnalysisData | null>(propData || null);
    const [loading, setLoading] = useState(!propData);

    // Update local state when prop changes (WebSocket update)
    useEffect(() => {
        if (propData) {
            setData(propData);
            setLoading(false);
        }
    }, [propData]);

    useEffect(() => {
        // Only fetch if no prop data is provided
        if (propData) return;

        const fetchAnalysis = async () => {
            try {
                // Assuming backend is on localhost:8000
                const response = await fetch('http://localhost:8000/api/analysis/latest');
                const result = await response.json();
                if (!result.error) {
                    setData(result);
                }
            } catch (error) {
                console.error("Failed to fetch AI analysis:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalysis();
        // Refresh every 5 minutes
        const interval = setInterval(fetchAnalysis, 300000);
        return () => clearInterval(interval);
    }, [propData]);

    if (loading) return <div className="p-4 text-center text-slate-500">Carregando análise...</div>;
    if (!data) return null;

    return (
        <Card className="w-full bg-slate-900/50 border-slate-800 text-slate-100 mb-6 backdrop-blur-sm">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-xl font-bold flex items-center gap-2 text-purple-400">
                            <Brain className="w-6 h-6" />
                            Jarvis Strategist
                        </CardTitle>
                        <div className="flex flex-col ml-8 mb-2">
                            <div className="flex items-center gap-2">
                                <span className="text-xs font-medium text-purple-300/70 uppercase tracking-wider">Análise Pré-Abertura</span>
                                <span className="text-xs text-slate-500">•</span>
                                <span className="text-xs text-slate-300 capitalize">
                                    {new Date().toLocaleDateString('pt-BR', { weekday: 'long', day: '2-digit', month: '2-digit', year: 'numeric' })}
                                </span>
                            </div>
                            {data.timestamp && (
                                <span className="text-xs text-slate-500">
                                    Atualizado às <span className="text-slate-300 font-mono">{data.timestamp}</span>
                                </span>
                            )}
                        </div>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    {/* Narrative */}
                    <div className="bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                        <h4 className="text-sm font-bold text-slate-400 mb-2 uppercase flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                            Narrativa do Dia
                        </h4>
                        <p className="text-slate-200 text-sm leading-relaxed italic border-l-2 border-purple-500 pl-3">
                            "{data.narrative}"
                        </p>
                    </div>

                    {/* Context Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        {/* WIN Context */}
                        <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
                            <div className="flex justify-between items-center mb-3 border-b border-slate-800 pb-2">
                                <h4 className="font-bold text-blue-400">WIN (Índice)</h4>
                                <Badge variant="outline" className="border-blue-900 text-blue-300">{data.win_context.bias}</Badge>
                            </div>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-slate-500 text-xs uppercase block">Estrutura</span>
                                    <span className="text-slate-300">{data.win_context.structure}</span>
                                </div>
                                <div>
                                    <span className="text-slate-500 text-xs uppercase block">Ímãs (Objetivos)</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {data.win_context.magnets.map((m, i) => (
                                            <span key={i} className="bg-blue-900/20 text-blue-300 px-2 py-0.5 rounded text-xs">{m}</span>
                                        ))}
                                    </div>
                                </div>
                                <div className="bg-yellow-900/10 border border-yellow-900/30 p-2 rounded">
                                    <div className="flex items-center gap-2 text-yellow-500 text-xs font-bold mb-1">
                                        <AlertTriangle className="w-3 h-3" /> ALERTA
                                    </div>
                                    <p className="text-xs text-yellow-200/80">{data.win_context.alert}</p>
                                </div>
                            </div>
                        </div>

                        {/* WDO Context */}
                        <div className="border border-slate-800 rounded-lg p-4 bg-slate-900/30">
                            <div className="flex justify-between items-center mb-3 border-b border-slate-800 pb-2">
                                <h4 className="font-bold text-green-400">WDO (Dólar)</h4>
                                <Badge variant="outline" className="border-green-900 text-green-300">{data.wdo_context.bias}</Badge>
                            </div>
                            <div className="space-y-3 text-sm">
                                <div>
                                    <span className="text-slate-500 text-xs uppercase block">Estrutura</span>
                                    <span className="text-slate-300">{data.wdo_context.structure}</span>
                                </div>
                                <div>
                                    <span className="text-slate-500 text-xs uppercase block">Ímãs (Objetivos)</span>
                                    <div className="flex flex-wrap gap-1 mt-1">
                                        {data.wdo_context.magnets.map((m, i) => (
                                            <span key={i} className="bg-green-900/20 text-green-300 px-2 py-0.5 rounded text-xs">{m}</span>
                                        ))}
                                    </div>
                                </div>
                                <div className="bg-yellow-900/10 border border-yellow-900/30 p-2 rounded">
                                    <div className="flex items-center gap-2 text-yellow-500 text-xs font-bold mb-1">
                                        <AlertTriangle className="w-3 h-3" /> ALERTA
                                    </div>
                                    <p className="text-xs text-yellow-200/80">{data.wdo_context.alert}</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Players Outlook */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="bg-slate-900/40 p-3 rounded border border-slate-800">
                            <h5 className="text-xs font-bold text-slate-400 uppercase mb-1">Estrangeiros</h5>
                            <p className="text-xs text-slate-300">{data.players_outlook.foreigners}</p>
                        </div>
                        <div className="bg-slate-900/40 p-3 rounded border border-slate-800">
                            <h5 className="text-xs font-bold text-slate-400 uppercase mb-1">Institucionais</h5>
                            <p className="text-xs text-slate-300">{data.players_outlook.institutions}</p>
                        </div>
                        <div className="bg-slate-900/40 p-3 rounded border border-slate-800">
                            <h5 className="text-xs font-bold text-slate-400 uppercase mb-1">Varejo (Risco)</h5>
                            <p className="text-xs text-slate-300">{data.players_outlook.retail_risk}</p>
                        </div>
                    </div>

                    {/* Executive Summary */}
                    <div className="bg-purple-900/20 border border-purple-900/50 p-3 rounded text-center">
                        <span className="text-purple-300 font-medium text-sm">"{data.executive_summary}"</span>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
