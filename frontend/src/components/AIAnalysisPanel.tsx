import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Brain, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';

interface Strategy {
    bias: string;
    gap_prediction: string;
    best_entry: string;
    trap_alert: string;
}

interface KeyLevels {
    resistance_major: number;
    resistance_minor?: number;
    pivot?: number;
    support_minor?: number;
    support_major: number;
}

interface Scenario {
    name: string;
    description: string;
}

interface AnalysisData {
    headline: string;
    market_mood: {
        sentiment: "RISK_ON" | "RISK_OFF" | "NEUTRO";
        score: number;
        main_driver: string;
    };
    opening_strategy: {
        win: Strategy;
        wdo: Strategy;
    };
    key_levels: {
        win: KeyLevels;
        wdo: KeyLevels;
    };
    scenarios: Scenario[];
    liquidity_radar: {
        warning: string;
        best_time_to_trade: string;
    };
    timestamp?: string;
}

const AIAnalysisPanel: React.FC = () => {
    const [data, setData] = useState<AnalysisData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalysis = async () => {
            try {
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
        const interval = setInterval(fetchAnalysis, 300000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-4 text-center text-gray-500">Carregando análise...</div>;
    if (!data) return null;

    const getMoodColor = (sentiment: string) => {
        switch (sentiment) {
            case 'RISK_ON': return 'text-green-400';
            case 'RISK_OFF': return 'text-red-400';
            default: return 'text-yellow-400';
        }
    };

    return (
        <Card className="w-full bg-slate-900 border-slate-800 text-slate-100 mb-6">
            <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-xl font-bold flex items-center gap-2 text-purple-400">
                            <Brain className="w-6 h-6" />
                            Jarvis Trader
                        </CardTitle>
                        <div className="flex items-center gap-2 mb-2 ml-8">
                            <p className="text-xs text-purple-300/70 font-medium">Insights Valiosos de Pré-Abertura</p>
                            {data.timestamp && (
                                <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
                                    Atualizado às {data.timestamp}
                                </span>
                            )}
                        </div>
                        <p className="text-sm text-slate-400 mt-1 border-l-2 border-purple-500 pl-2 italic">{data.headline}</p>
                    </div>
                    <div className="text-right">
                        <Badge className={`${getMoodColor(data.market_mood.sentiment)} bg-slate-800 border-slate-700`}>
                            {data.market_mood.sentiment} ({data.market_mood.score})
                        </Badge>
                        <div className="text-xs text-slate-500 mt-1">{data.market_mood.main_driver}</div>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-6">
                    {/* Strategies Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {/* WIN Strategy */}
                        <div className="bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                            <div className="flex justify-between items-center mb-3">
                                <h4 className="font-bold text-blue-400">WIN (Índice)</h4>
                                <span className="text-xs bg-blue-900/30 text-blue-300 px-2 py-1 rounded">{data.opening_strategy.win.bias}</span>
                            </div>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between"><span className="text-slate-500">Gap:</span> <span>{data.opening_strategy.win.gap_prediction}</span></div>
                                <div className="flex justify-between"><span className="text-slate-500">Entrada:</span> <span className="text-green-300">{data.opening_strategy.win.best_entry}</span></div>
                                <div className="bg-red-900/10 border border-red-900/30 p-2 rounded mt-2">
                                    <div className="flex items-center gap-2 text-red-400 text-xs font-bold"><AlertTriangle className="w-3 h-3" /> ARMADILHA</div>
                                    <div className="text-xs text-red-300">{data.opening_strategy.win.trap_alert}</div>
                                </div>
                            </div>
                        </div>

                        {/* WDO Strategy */}
                        <div className="bg-slate-950/50 p-4 rounded-lg border border-slate-800">
                            <div className="flex justify-between items-center mb-3">
                                <h4 className="font-bold text-green-400">WDO (Dólar)</h4>
                                <span className="text-xs bg-green-900/30 text-green-300 px-2 py-1 rounded">{data.opening_strategy.wdo.bias}</span>
                            </div>
                            <div className="space-y-2 text-sm">
                                <div className="flex justify-between"><span className="text-slate-500">Gap:</span> <span>{data.opening_strategy.wdo.gap_prediction}</span></div>
                                <div className="flex justify-between"><span className="text-slate-500">Entrada:</span> <span className="text-green-300">{data.opening_strategy.wdo.best_entry}</span></div>
                                <div className="bg-red-900/10 border border-red-900/30 p-2 rounded mt-2">
                                    <div className="flex items-center gap-2 text-red-400 text-xs font-bold"><AlertTriangle className="w-3 h-3" /> ARMADILHA</div>
                                    <div className="text-xs text-red-300">{data.opening_strategy.wdo.trap_alert}</div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Scenarios & Radar */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className="md:col-span-2 space-y-2">
                            <h4 className="text-sm font-semibold text-slate-400">Cenários</h4>
                            {data.scenarios.map((scenario, idx) => (
                                <div key={idx} className="bg-slate-800/50 p-3 rounded border-l-2 border-purple-500">
                                    <div className="font-bold text-sm text-slate-200">{scenario.name}</div>
                                    <div className="text-xs text-slate-400">{scenario.description}</div>
                                </div>
                            ))}
                        </div>
                        <div className="space-y-2">
                            <h4 className="text-sm font-semibold text-slate-400">Radar de Liquidez</h4>
                            <div className="bg-slate-800/50 p-3 rounded h-full flex flex-col justify-center">
                                <div className="text-xs text-yellow-400 mb-2 font-bold">{data.liquidity_radar.warning}</div>
                                <div className="text-xs text-slate-300">
                                    <span className="block text-slate-500 mb-1">Melhor Horário:</span>
                                    {data.liquidity_radar.best_time_to_trade}
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default AIAnalysisPanel;
