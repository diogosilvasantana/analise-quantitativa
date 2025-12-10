import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Lock, Activity, Users, TrendingUp, TrendingDown } from 'lucide-react';

import { DashboardData } from '@/types/dashboard';

// ... imports remain the same

interface QuantPanelProps {
    data: DashboardData | null;
    asset?: 'WIN' | 'WDO'; // Optional asset filter
}

const QuantPanel: React.FC<QuantPanelProps> = ({ data, asset }) => {
    const quantData = data?.quant_dashboard;
    const scores = quantData?.score || {};
    const flows = quantData?.flows || {};

    // Default empty flow/score if missing
    const winFlow = flows.WIN || { FOREIGN: 0, INSTITUTIONAL: 0, RETAIL: 0 };
    const wdoFlow = flows.WDO || { FOREIGN: 0, INSTITUTIONAL: 0, RETAIL: 0 };

    const winScore = scores.WIN?.score || 0;
    const wdoScore = scores.WDO?.score || 0;
    const maxScore = 15;

    // ... helper functions (getScoreColor, etc) remain the same

    const getScoreColor = (s: number) => {
        if (s >= 10) return "text-green-400";
        if (s >= 7) return "text-yellow-400";
        return "text-red-400";
    };

    const getBarColor = (val: number) => val > 0 ? "bg-blue-500" : "bg-red-500";
    const getWidth = (val: number) => Math.min(Math.abs(val) / 20, 100); // Scale factor

    const getStatusLabel = (val: number) => {
        if (val > 0) return <span className="text-blue-400 text-[10px] font-bold">COMPRADOR</span>;
        if (val < 0) return <span className="text-red-400 text-[10px] font-bold">VENDEDOR</span>;
        return <span className="text-slate-500 text-[10px]">NEUTRO</span>;
    };

    const renderScoreCard = (title: string, score: number, marketStatus?: string) => (
        <div className="flex items-center justify-between mb-2 bg-slate-800/50 p-2 rounded-lg border border-slate-700/50">
            <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">{title}</p>
                <div className="flex items-baseline gap-1">
                    <span className={`text-xl font-bold ${getScoreColor(score)}`}>{score}</span>
                    <span className="text-[10px] text-slate-500">/{maxScore}</span>
                </div>
            </div>
            <div className="text-right flex flex-col items-end gap-1">
                <Badge className={
                    score >= 10 ? "bg-green-500/20 text-green-400 text-[10px] px-1" :
                        score <= 5 ? "bg-red-500/20 text-red-400 text-[10px] px-1" :
                            "bg-yellow-500/20 text-yellow-400 text-[10px] px-1"
                }>
                    {score >= 10 ? "COMPRA FORTE" : score >= 7 ? "COMPRA" : score <= 5 ? "VENDA" : "NEUTRO"}
                </Badge>
                {/* Show status in single view if available */}
                {asset && marketStatus && (
                    <Badge variant="outline" className={`text-[10px] border-0 px-1 ${marketStatus === 'OPEN' ? 'text-green-500' : 'text-slate-500'}`}>
                        {marketStatus === 'OPEN' ? '● ABERTO' : '● FECHADO'}
                    </Badge>
                )}
            </div>
        </div>
    );

    const renderFlowColumn = (title: string, flow: any, score: number, marketStatus?: string) => (
        <div className="flex-1 space-y-3">
            {!asset && renderScoreCard(`Score ${title}`, score)} {/* Show integrated score card if not in single asset mode, or customize logic */}
            {asset && renderScoreCard(`Score Quant`, score, marketStatus)}

            <h4 className="text-xs font-bold text-slate-300 border-b border-slate-700 pb-1 mb-2">Fluxo Acumulado</h4>

            {/* Foreign */}
            <div className="space-y-1">
                <div className="flex justify-between text-xs items-center">
                    <span className="text-slate-400">Gringo</span>
                    {getStatusLabel(flow.FOREIGN)}
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden flex">
                    <div className={`h-full transition-all duration-500 ${getBarColor(flow.FOREIGN)}`}
                        style={{ width: `${getWidth(flow.FOREIGN)}%`, marginLeft: flow.FOREIGN < 0 ? 'auto' : '0' }} />
                </div>
                <div className="text-[10px] text-right text-slate-500">{flow.FOREIGN}</div>
            </div>

            {/* Institutional */}
            <div className="space-y-1">
                <div className="flex justify-between text-xs items-center">
                    <span className="text-slate-400">Inst.</span>
                    {getStatusLabel(flow.INSTITUTIONAL)}
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden flex">
                    <div className={`h-full transition-all duration-500 ${getBarColor(flow.INSTITUTIONAL)}`}
                        style={{ width: `${getWidth(flow.INSTITUTIONAL)}%`, marginLeft: flow.INSTITUTIONAL < 0 ? 'auto' : '0' }} />
                </div>
                <div className="text-[10px] text-right text-slate-500">{flow.INSTITUTIONAL}</div>
            </div>

            {/* Retail */}
            <div className="space-y-1">
                <div className="flex justify-between text-xs items-center">
                    <span className="text-slate-400">Varejo</span>
                    {getStatusLabel(flow.RETAIL)}
                </div>
                <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden flex">
                    <div className={`h-full transition-all duration-500 ${getBarColor(flow.RETAIL)}`}
                        style={{ width: `${getWidth(flow.RETAIL)}%`, marginLeft: flow.RETAIL < 0 ? 'auto' : '0' }} />
                </div>
                <div className="text-[10px] text-right text-slate-500">{flow.RETAIL}</div>
            </div>
        </div>
    );

    // If asset mode, return bare content without Card wrapper
    if (asset) {
        return (
            <div className="h-full">
                {asset === 'WIN' ? (
                    renderFlowColumn("WIN", winFlow, winScore, scores.WIN?.market_status)
                ) : (
                    renderFlowColumn("WDO", wdoFlow, wdoScore, scores.WDO?.market_status)
                )}
            </div>
        );
    }

    return (
        <Card className="bg-slate-900 border-slate-800 h-full relative overflow-hidden">
            {/* Default Split View Header */}
            <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                    <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                        <Activity className="w-4 h-4 text-blue-400" />
                        Quant Dashboard
                    </CardTitle>
                </div>
            </CardHeader>

            <CardContent>
                {/* Default Split View: WIN vs WDO */}
                <div className="flex gap-4">
                    {renderFlowColumn("WIN", winFlow, winScore, scores.WIN?.market_status)}
                    <div className="w-px bg-slate-800" />
                    {renderFlowColumn("WDO", wdoFlow, wdoScore, scores.WDO?.market_status)}
                </div>
            </CardContent>
        </Card>
    );
};

export default QuantPanel;


