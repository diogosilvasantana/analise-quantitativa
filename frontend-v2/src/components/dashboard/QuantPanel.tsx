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
    const scores = quantData?.score || {};
    const flows = quantData?.flows || {};

    // Default empty flow/score if missing
    const winFlow = flows.WIN || { FOREIGN: 0, INSTITUTIONAL: 0, RETAIL: 0 };
    const wdoFlow = flows.WDO || { FOREIGN: 0, INSTITUTIONAL: 0, RETAIL: 0 };

    const winScore = scores.WIN?.score || 0;
    const wdoScore = scores.WDO?.score || 0;
    const maxScore = 15;

    // Score Color
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

    const renderScoreCard = (title: string, score: number) => (
        <div className="flex items-center justify-between mb-2 bg-slate-800/50 p-2 rounded-lg border border-slate-700/50">
            <div>
                <p className="text-[10px] text-slate-500 uppercase tracking-wider mb-1">{title}</p>
                <div className="flex items-baseline gap-1">
                    <span className={`text-xl font-bold ${getScoreColor(score)}`}>{score}</span>
                    <span className="text-[10px] text-slate-500">/{maxScore}</span>
                </div>
            </div>
            <div className="text-right">
                <Badge className={score >= 7 ? "bg-green-500/20 text-green-400 text-[10px] px-1" : "bg-slate-700 text-slate-400 text-[10px] px-1"}>
                    {score >= 7 ? "COMPRA" : "NEUTRO"}
                </Badge>
            </div>
        </div>
    );

    const renderFlowColumn = (title: string, flow: any, score: number) => (
        <div className="flex-1 space-y-3">
            {renderScoreCard(`Score ${title}`, score)}

            <h4 className="text-xs font-bold text-slate-300 border-b border-slate-700 pb-1 mb-2">{title}</h4>

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
                {/* Split View: WIN vs WDO */}
                <div className="flex gap-4">
                    {renderFlowColumn("WIN", winFlow, winScore)}
                    <div className="w-px bg-slate-800" /> {/* Divider */}
                    {renderFlowColumn("WDO", wdoFlow, wdoScore)}
                </div>
            </CardContent>
        </Card>
    );
};

export default QuantPanel;
