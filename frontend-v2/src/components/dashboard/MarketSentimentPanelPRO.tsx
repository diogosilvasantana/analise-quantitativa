'use client';

import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';

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

    const basisMap: Record<string, string> = {
        PREMIUM_HIGH: 'Otimismo Exagerado 🚀',
        PREMIUM_NORMAL: 'Prêmio Normal ✅',
        FLAT: 'Indecisão 😐',
        DISCOUNT: 'Desconto (Backwardation) 📉',
        DISCOUNT_HIGH: 'Pessimismo Extremo 💀',
    };

    const signalMap: Record<string, string> = {
        STRONG_BUY: 'Compra Forte 🐂',
        STRONG_SELL: 'Venda Forte 🐻',
        BULLISH_DIVERGENCE: 'Divergência Altista 💎',
        BEARISH_DIVERGENCE: 'Divergência Baixista ⚠️',
        BUY: 'Compra 📈',
        SELL: 'Venda 📉',
        NEUTRAL: 'Neutro 😐',
    };

    const getBasisLabel = (key: string) => basisMap[key] || key;
    const getSignalLabel = (key: string) => signalMap[key] || key;

    const isBullish = breadth?.signal?.includes('BUY') || false;
    const isBearish = breadth?.signal?.includes('SELL') || false;
    const hasDivergence = sentiment_comparison?.divergence || false;

    if (!data) return null;

    return (
        <div className="space-y-6">
            {/* ALERT BANNER */}
            {hasDivergence && (
                <Alert className="border-red-500/50 bg-red-950/30 animate-pulse">
                    <AlertDescription className="flex items-center gap-2 text-red-400">
                        <span className="text-lg">⚠️</span>
                        <span>
                            DIVERGÊNCIA: {getSignalLabel(sentiment_comparison?.spx_signal || '')} vs{' '}
                            {getSignalLabel(sentiment_comparison?.win_signal || '')}
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
                                'text-4xl md:text-5xl font-black tracking-tight',
                                isBullish && 'bg-gradient-to-r from-emerald-400 to-emerald-500 bg-clip-text text-transparent drop-shadow-lg',
                                isBearish && 'text-red-400 drop-shadow-lg',
                                !isBullish && !isBearish && 'text-slate-400'
                            )}
                        >
                            {getSignalLabel(breadth.signal)}
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
                        <div className="text-sm text-emerald-400 font-semibold">{getBasisLabel(basis.interpretation)}</div>
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
                                <div className="font-bold text-emerald-400">{breadth.up}</div>
                                <div className="text-slate-500">Altas</div>
                            </div>
                            <div className="text-center">
                                <div className="font-bold text-slate-400">{breadth.neutral}</div>
                                <div className="text-slate-500">Neutras</div>
                            </div>
                            <div className="text-center">
                                <div className="font-bold text-red-400">{breadth.down}</div>
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
                                        'text-sm font-bold',
                                        sentiment_comparison.spx_signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {getSignalLabel(sentiment_comparison.spx_signal)}
                                </div>
                            </div>
                            <div className="text-xl px-2">{hasDivergence ? '⚠️' : '✅'}</div>
                            <div className="text-center flex-1">
                                <div className="text-xs text-slate-500 mb-1">WIN</div>
                                <div
                                    className={cn(
                                        'text-sm font-bold',
                                        sentiment_comparison.win_signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {getSignalLabel(sentiment_comparison.win_signal)}
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
                        {signal_history.slice().reverse().slice(0, 5).map((item, idx) => (
                            <div key={idx} className="flex items-center justify-between p-2 bg-slate-900/30 rounded border border-slate-700/50">
                                <span className="text-xs font-mono text-slate-500">{item.time}</span>
                                <span
                                    className={cn(
                                        'text-xs font-bold',
                                        item.signal.includes('BUY') ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {getSignalLabel(item.signal)}
                                </span>
                            </div>
                        ))}
                    </div>
                </Card>
            )}
        </div>
    );
}
