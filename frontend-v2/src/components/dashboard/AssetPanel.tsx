import React from 'react';
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertTriangle, TrendingUp, TrendingDown, Minus, Activity } from 'lucide-react';
import { DashboardData } from '@/types/dashboard';
import { AIContextCard } from './AIAnalysisPanel';
import QuantPanel from './QuantPanel';
import MarketThermometer from './MarketThermometer';

interface AssetPanelProps {
    asset: 'WIN' | 'WDO';
    data: DashboardData | null;
}

export function AssetPanel({ asset, data }: AssetPanelProps) {
    // Extract asset-specific data
    const quantScore = data?.quant_dashboard?.score?.[asset];
    const context = asset === 'WIN' ? data?.ai_analysis?.win_context : data?.ai_analysis?.wdo_context;

    // Theme Colors
    const isWin = asset === 'WIN';
    const primaryColor = isWin ? 'text-blue-400' : 'text-green-400';
    const borderColor = isWin ? 'border-blue-900/30' : 'border-green-900/30';
    const bgGradient = isWin ? 'from-blue-950/20 to-slate-900/50' : 'from-green-950/20 to-slate-900/50';

    return (
        <div className={`h-full flex flex-col gap-0 border border-slate-800 rounded-xl overflow-hidden bg-gradient-to-b ${bgGradient}`}>

            {/* 1. Header & Live Status */}
            <div className="flex items-center justify-between p-4 border-b border-slate-800/50 bg-slate-900/50">
                <div className="flex items-center gap-3">
                    <div className={`p-2 rounded-lg bg-slate-800 ${borderColor} border`}>
                        {isWin ? <Activity className="w-5 h-5 text-blue-400" /> : <Activity className="w-5 h-5 text-green-400" />}
                    </div>
                    <div>
                        <h2 className={`text-xl font-bold ${primaryColor} leading-none`}>
                            {isWin ? 'ÍNDICE (WIN)' : 'DÓLAR (WDO)'}
                        </h2>
                        <span className="text-xs text-slate-500 font-mono tracking-wider">
                            {quantScore?.market_status === 'OPEN' ? 'MERCADO ABERTO' : 'MERCADO FECHADO'}
                        </span>
                    </div>
                </div>

                {/* Mini Thermometer Display */}
                <div className="flex items-center gap-4">
                    <div className="flex flex-col items-end">
                        <span className="text-xs text-slate-400 uppercase">Força</span>
                        <div className="flex items-center gap-2">
                            <div className="flex items-center gap-1 text-red-400 text-sm font-bold">
                                <TrendingDown className="w-3 h-3" /> {quantScore?.bear_power || 0}
                            </div>
                            <div className="h-4 w-px bg-slate-700"></div>
                            <div className="flex items-center gap-1 text-green-400 text-sm font-bold">
                                {quantScore?.bull_power || 0} <TrendingUp className="w-3 h-3" />
                            </div>
                        </div>
                    </div>
                    {/* Gauge Ring (Simplified/Canvas could go here, but using Score Badge for now) */}
                    <Badge variant="outline" className={`${isWin ? 'border-blue-500/30 text-blue-400' : 'border-green-500/30 text-green-400'} text-lg px-3 py-1`}>
                        {quantScore?.score || 0}<span className="text-xs ml-1 opacity-50">/15</span>
                    </Badge>
                </div>
            </div>

            {/* 2. AI Context Strip */}
            <div className="px-4 py-3 bg-slate-900/30 border-b border-slate-800/50 flex flex-wrap gap-4 items-center min-h-[60px]">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-bold text-slate-500 uppercase">Viés IA:</span>
                    <Badge className={isWin ? 'bg-blue-900/20 text-blue-300 border-blue-900' : 'bg-green-900/20 text-green-300 border-green-900'}>
                        {context?.bias || 'NEUTRO'}
                    </Badge>
                </div>

                <div className="h-4 w-px bg-slate-800"></div>

                <div className="flex flex-1 items-center gap-2 overflow-hidden">
                    <span className="text-xs font-bold text-slate-500 uppercase whitespace-nowrap">Alvos:</span>
                    <div className="flex flex-wrap gap-1">
                        {context?.magnets?.map((m, i) => (
                            <span key={i} className="text-xs font-mono text-slate-300 bg-slate-800/50 px-1.5 rounded">{m}</span>
                        )) || <span className="text-xs text-slate-600">-</span>}
                    </div>
                </div>

                {context?.alert && (
                    <div className="flex items-center gap-2 text-yellow-500 animate-pulse">
                        <AlertTriangle className="w-4 h-4" />
                        <span className="text-xs font-bold uppercase hidden xl:inline">Alerta</span>
                    </div>
                )}
            </div>

            {/* 3. Main Quant Flow */}
            <div className="flex-1 p-0 overflow-hidden relative">
                {/* Re-using QuantPanel in 'asset' mode which separates visuals. 
                     Ideally we would strip the QuantPanel card wrapper, but for now we let it fill. */}
                <div className="absolute inset-0 overflow-y-auto custom-scrollbar">
                    <div className="p-4 h-full">
                        <QuantPanel data={data} asset={asset} />
                    </div>
                </div>
            </div>

            {/* Optional Footer Details if needed */}
        </div>
    );
}
