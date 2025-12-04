'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';
import {
    Rocket,
    CheckCircle2,
    MinusCircle,
    TrendingDown,
    TrendingUp,
    AlertTriangle,
    Skull,
    Diamond,
    ArrowUp,
    ArrowDown,
    Minus
} from 'lucide-react';

interface MarketSentimentPanelPROProps {
    data: DashboardData;
}

export function MarketSentimentPanelPRO({ data }: MarketSentimentPanelPROProps) {
    const [statusChanged, setStatusChanged] = useState(false);

    const { basis, breadth, sentiment_comparison, signal_history } = data || {};

    useEffect(() => {
        setStatusChanged(true);
        const timer = setTimeout(() => setStatusChanged(false), 1500);
        return () => clearTimeout(timer);
    }, [sentiment_comparison?.status, basis?.value]);

    const basisMap: Record<string, { label: string; icon: React.ReactNode }> = {
        PREMIUM_HIGH: { label: 'Otimismo Exagerado', icon: <Rocket className="w-4 h-4" /> },
        PREMIUM_NORMAL: { label: 'Prêmio Normal', icon: <CheckCircle2 className="w-4 h-4" /> },
        FLAT: { label: 'Indecisão', icon: <MinusCircle className="w-4 h-4" /> },
        DISCOUNT: { label: 'Desconto (Backwardation)', icon: <TrendingDown className="w-4 h-4" /> },
        DISCOUNT_HIGH: { label: 'Pessimismo Extremo', icon: <Skull className="w-4 h-4" /> },
    };

    const signalMap: Record<string, { label: string; icon: React.ReactNode }> = {
        STRONG_BUY: { label: 'Compra Forte', icon: <TrendingUp className="w-5 h-5" /> },
        STRONG_SELL: { label: 'Venda Forte', icon: <TrendingDown className="w-5 h-5" /> },
        BULLISH_DIVERGENCE: { label: 'Divergência Altista', icon: <Diamond className="w-5 h-5" /> },
        BEARISH_DIVERGENCE: { label: 'Divergência Baixista', icon: <AlertTriangle className="w-5 h-5" /> },
        BUY: { label: 'Compra', icon: <TrendingUp className="w-5 h-5" /> },
        SELL: { label: 'Venda', icon: <TrendingDown className="w-5 h-5" /> },
        NEUTRAL: { label: 'Neutro', icon: <MinusCircle className="w-5 h-5" /> },
    };

    const getBasisInfo = (key: string) => basisMap[key] || { label: key, icon: null };
    const getSignalInfo = (key: string) => signalMap[key] || { label: key, icon: null };

    const isBullish = breadth?.signal?.includes('BUY') || false;
    const isBearish = breadth?.signal?.includes('SELL') || false;
    const hasDivergence = sentiment_comparison?.divergence || false;

    if (!data) return null;

    const spxInfo = getSignalInfo(sentiment_comparison?.spx_signal || '');
    const winInfo = getSignalInfo(sentiment_comparison?.win_signal || '');
    const breadthInfo = getSignalInfo(breadth?.signal || '');

    return (
        <div className="space-y-6">
            {/* ALERT BANNER */}
            {hasDivergence && (
                <Alert className="border-red-500/50 bg-red-950/30 animate-pulse">
                    <AlertDescription className="flex items-center gap-2 text-red-400">
                        <AlertTriangle className="w-5 h-5" />
                        <span>
                            DIVERGÊNCIA: {spxInfo.label} vs {winInfo.label}
                        </span>
                    </AlertDescription>
                </Alert>
            )}

            {/* SIGNAL HERO */}
            {breadth && (
                <Card className="border-slate-700 bg-gradient-to-br from-slate-800/50 to-slate-900/50 p-8 overflow-hidden relative">
                    <div
                        className={cn(
                            'text-center space-y-4 relative z-10',
                            isBullish && 'animate-pulse',
                            isBearish && 'animate-pulse'
                        )}
                    >
                        <div
                            className={cn(
                                'text-4xl md:text-5xl font-black tracking-tight flex items-center justify-center gap-3',
                                isBullish && 'bg-gradient-to-r from-emerald-400 to-emerald-500 bg-clip-text text-transparent drop-shadow-lg',
                                isBearish && 'text-red-400 drop-shadow-lg',
                                !isBullish && !isBearish && 'text-slate-400'
                            )}
                        >
                            {breadthInfo.icon}
                            {breadthInfo.label}
                        </div>
                        <div
                            className={cn(
                                'text-lg font-semibold',
                                statusChanged ? 'animate-pulse' : '',
                                isBullish ? 'text-emerald-400' : isBearish ? 'text-red-400' : 'text-cyan-400'
                            )}
                        >
                            Confiança: {breadth.confidence.toFixed(0)}%
                        </div>
                    </div>

                    {/* Decorative background */}
                    {isBullish && (
                        <div className="absolute inset-0 bg-gradient-to-r from-emerald-500/10 to-transparent opacity-30 blur-3xl" />
                    )}
                    {isBearish && (
                        <div className="absolute inset-0 bg-gradient-to-r from-red-500/10 to-transparent opacity-30 blur-3xl" />
                    )}
                </Card>
            )}

            {/* METRICS GRID */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* BASIS CARD */}
                {basis && (
                    <Card className="border-slate-700 bg-slate-800/30 p-6 hover:border-emerald-500/50 transition-colors">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Basis (Futuro vs À Vista)</h3>
                        <div className="text-3xl font-bold text-emerald-400 font-mono mb-4">
                            {basis.value > 0 ? '+' : ''}{basis.value.toFixed(0)} pts
                        </div>
                        <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden mb-4">
                            <div
                                className="h-full bg-gradient-to-r from-emerald-500 to-cyan-500 transition-all duration-500"
                                style={{ width: `${Math.max(0, Math.min(100, (basis.value + 2000) / 40))}%` }}
                            />
                        </div>
                        <div className="text-sm text-emerald-400 font-semibold flex items-center gap-2">
                            {getBasisInfo(basis.interpretation).icon}
                            {getBasisInfo(basis.interpretation).label}
                        </div>
                    </Card>
                )}

                {/* BREADTH CARD */}
                {breadth && (
                    <Card className="border-slate-700 bg-slate-800/30 p-6 hover:border-emerald-500/50 transition-colors">
                        <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Força do Movimento (Top 10)</h3>
                        <div className="flex items-end gap-2 h-24 mb-4">
                            <div className="flex-1 bg-gradient-to-t from-emerald-500 to-emerald-600 rounded h-full opacity-80" style={{ height: `${(breadth.up / 10) * 100}%` }} />
                            <div className="flex-1 bg-gradient-to-t from-slate-600 to-slate-700 rounded h-full opacity-60" style={{ height: `${(breadth.neutral / 10) * 100}%` }} />
                            <div className="flex-1 bg-gradient-to-t from-red-500 to-red-600 rounded h-full opacity-80" style={{ height: `${(breadth.down / 10) * 100}%` }} />
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs">
                            <div className="text-center">
                                <div className="font-bold text-emerald-400 flex items-center justify-center gap-1">
                                    <ArrowUp className="w-3 h-3" /> {breadth.up}
                                </div>
                                <div className="text-slate-500">Altas</div>
                            </div>
                            <div className="text-center">
                                <div className="font-bold text-slate-400 flex items-center justify-center gap-1">
                                    <Minus className="w-3 h-3" /> {breadth.neutral}
                                </div>
                                <div className="text-slate-500">Neutras</div>
                            </div>
                            <div className="text-center">
                                <div className="font-bold text-red-400 flex items-center justify-center gap-1">
                                    <ArrowDown className="w-3 h-3" /> {breadth.down}
                                </div>
                                <div className="text-slate-500">Baixas</div>
                            </div>
                        </div>
                    </Card>
                )}

                {/* COMPARISON CARD */}
                {sentiment_comparison && (
                    <Card
                        className={cn(
                            'border-slate-700 bg-slate-800/30 p-6 transition-all',
                            hasDivergence && 'border-red-500/50 bg-red-950/20 animate-pulse'
                        )}
                    >
                        <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">SPX vs WIN</h3>
                        <div className="flex items-center justify-between mb-4">
                            <div className="text-center flex-1">
                                <div className="text-xs text-slate-500 mb-1">S&P 500</div>
                                <div
                                    className={cn(
                                        'text-sm font-bold flex items-center justify-center gap-1',
                                        sentiment_comparison.spx_signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {spxInfo.icon}
                                    {spxInfo.label}
                                </div>
                            </div>
                            <div className="text-xl px-2">
                                {hasDivergence ? <AlertTriangle className="w-6 h-6 text-yellow-500" /> : <CheckCircle2 className="w-6 h-6 text-emerald-500" />}
                            </div>
                            <div className="text-center flex-1">
                                <div className="text-xs text-slate-500 mb-1">WIN</div>
                                <div
                                    className={cn(
                                        'text-sm font-bold flex items-center justify-center gap-1',
                                        sentiment_comparison.win_signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {winInfo.icon}
                                    {winInfo.label}
                                </div>
                            </div>
                        </div>
                        <div
                            className={cn(
                                'text-xs font-semibold text-center py-2 rounded',
                                sentiment_comparison.status === 'ALINHADO'
                                    ? 'bg-emerald-500/20 text-emerald-400'
                                    : 'bg-yellow-500/20 text-yellow-400'
                            )}
                        >
                            {sentiment_comparison.status}
                        </div>
                    </Card>
                )}
            </div>

            {/* TIMELINE */}
            {signal_history && signal_history.length > 0 && (
                <Card className="border-slate-700 bg-slate-800/30 p-6">
                    <h3 className="text-sm font-semibold text-slate-400 uppercase mb-4">Histórico de Sinais</h3>
                    <div className="space-y-2">
                        {signal_history.slice().reverse().slice(0, 5).map((item, idx) => {
                            const info = getSignalInfo(item.signal);
                            return (
                                <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-700/50">
                                    <span className="text-xs font-mono text-slate-500">{item.time}</span>
                                    <span
                                        className={cn(
                                            'text-xs font-bold flex items-center gap-1',
                                            item.signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                        )}
                                    >
                                        {info.icon}
                                        {info.label}
                                    </span>
                                </div>
                            );
                        })}
                    </div>
                </Card>
            )}
        </div>
    );
}
