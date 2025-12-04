'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';

const INDICES_NAMES: Record<string, string> = {
    SP500: 'S&P 500',
    NASDAQ: 'Nasdaq 100',
    DOW_JONES: 'Dow Jones',
    DXY: 'Dólar Index',
    DAX40: 'DAX 40 (Alemanha)',
    US10Y: 'Treasury 10Y',
    EWZ: 'EWZ (Brasil ETF)',
};

interface IndicePanelProps {
    data: DashboardData;
}

export function IndicesPanel({ data }: IndicePanelProps) {
    if (!data?.indices_globais) return null;

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4">Índices Globais 🌍</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(data.indices_globais).map(([ticker, indice]) => (
                    indice && (
                        <div
                            key={ticker}
                            className={cn(
                                'p-4 rounded-lg border transition-all hover:border-slate-600',
                                indice.var >= 0
                                    ? 'border-emerald-500/30 bg-emerald-950/20'
                                    : 'border-red-500/30 bg-red-950/20'
                            )}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-slate-300">{INDICES_NAMES[ticker] || ticker}</h3>
                                <span className="text-xs text-slate-500">{ticker}</span>
                            </div>
                            <div className="text-lg font-bold text-slate-100 mb-1 font-mono">
                                {indice.valor.toFixed(2)}
                            </div>
                            <div
                                className={cn(
                                    'text-sm font-semibold',
                                    indice.var >= 0 ? 'text-emerald-400' : 'text-red-400'
                                )}
                            >
                                {indice.var >= 0 ? '📈' : '📉'} {indice.var_pct.toFixed(2)}%
                            </div>
                        </div>
                    )
                ))}
            </div>
        </Card>
    );
}
