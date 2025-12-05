import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Lock, Activity, Users, TrendingUp, TrendingDown } from 'lucide-react';

interface QuantPanelProps {
    data: any; // Using any for flexibility, ideally strictly typed
}

const QuantPanel: React.FC<QuantPanelProps> = ({ data }) => {
    const quantData = data?.quant_dashboard;
    const score = quantData?.score?.score || 0;
    const maxScore = 15;
    const flow = quantData?.flow || { FOREIGN: 0, INSTITUTIONAL: 0, RETAIL: 0 };

    // 10h Rule Logic - REMOVED (Always Open)
    const isBefore10 = false;

    // Score Color
    const getScoreColor = (s: number) => {
        if (s >= 10) return "text-green-400";
        if (s >= 7) return "text-yellow-400";
        return "text-red-400";
    };

    const getBarColor = (val: number) => val > 0 ? "bg-blue-500" : "bg-red-500";
    const getWidth = (val: number) => Math.min(Math.abs(val) / 20, 100); // Scale factor

    return (
        <Card className="bg-slate-900 border-slate-800 h-full relative overflow-hidden">
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-blue-400" />
                        Quant Dashboard
                    </CardTitle>
                </div>
            </CardHeader>

            <CardContent>
                {/* Score Card */}
                <div className="flex items-center justify-between mb-6 bg-slate-800/50 p-4 rounded-lg border border-slate-700/50">
                    <div>
                        <p className="text-xs text-slate-500 uppercase tracking-wider mb-1">Score Quant</p>
                        <div className="flex items-baseline gap-1">
                            <span className={`text-3xl font-bold ${getScoreColor(score)}`}>{score}</span>
                            <span className="text-sm text-slate-500">/{maxScore}</span>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-slate-500 mb-1">Status</p>
                        <Badge className={score >= 7 ? "bg-green-500/20 text-green-400" : "bg-slate-700 text-slate-400"}>
                            {score >= 7 ? "COMPRA AUTORIZADA" : "NEUTRO / AGUARDANDO"}
                        </Badge>
                    </div>
                </div>

                {/* Player Flow */}
                <div className="space-y-4">
                    <div className="flex items-center gap-2 mb-2">
                        <Users className="w-4 h-4 text-slate-400" />
                        <span className="text-xs font-medium text-slate-300">Fluxo de Players (Saldo)</span>
                    </div>

                    {/* Foreign */}
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-400">Estrangeiros (Gringo)</span>
                            <span className={flow.FOREIGN > 0 ? "text-blue-400" : "text-red-400"}>
                                {flow.FOREIGN > 0 ? "+" : ""}{flow.FOREIGN}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                            <div className={`h-full transition-all duration-500 ${getBarColor(flow.FOREIGN)}`}
                                style={{ width: `${getWidth(flow.FOREIGN)}%`, marginLeft: flow.FOREIGN < 0 ? 'auto' : '0' }} />
                        </div>
                    </div>

                    {/* Institutional */}
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-400">Institucionais</span>
                            <span className={flow.INSTITUTIONAL > 0 ? "text-blue-400" : "text-red-400"}>
                                {flow.INSTITUTIONAL > 0 ? "+" : ""}{flow.INSTITUTIONAL}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                            <div className={`h-full transition-all duration-500 ${getBarColor(flow.INSTITUTIONAL)}`}
                                style={{ width: `${getWidth(flow.INSTITUTIONAL)}%`, marginLeft: flow.INSTITUTIONAL < 0 ? 'auto' : '0' }} />
                        </div>
                    </div>

                    {/* Retail */}
                    <div className="space-y-1">
                        <div className="flex justify-between text-xs">
                            <span className="text-slate-400">Varejo (Pessoa Física)</span>
                            <span className={flow.RETAIL > 0 ? "text-blue-400" : "text-red-400"}>
                                {flow.RETAIL > 0 ? "+" : ""}{flow.RETAIL}
                            </span>
                        </div>
                        <div className="h-2 bg-slate-800 rounded-full overflow-hidden flex">
                            <div className={`h-full transition-all duration-500 ${getBarColor(flow.RETAIL)}`}
                                style={{ width: `${getWidth(flow.RETAIL)}%`, marginLeft: flow.RETAIL < 0 ? 'auto' : '0' }} />
                        </div>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
};

export default QuantPanel;
