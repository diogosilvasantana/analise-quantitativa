'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const INDICES_CONFIG: Record<string, { name: string }> = {
    SP500: { name: 'S&P 500' },
    NASDAQ: { name: 'Nasdaq' },
    DOW_JONES: { name: 'Dow Jones' },
    DXY: { name: 'DXY' },
    DAX40: { name: 'DAX' },
    US10Y: { name: 'US10Y' },
    EWZ: { name: 'EWZ' },
    BRENT: { name: 'Brent' },
    OURO: { name: 'Ouro' },
    MINERIO_FERRO: { name: 'Minério' },
    BITCOIN: { name: 'Bitcoin' },
};

interface IndicePanelProps {
    data: DashboardData;
}

export function IndicesPanel({ data }: IndicePanelProps) {
    if (!data?.indices_globais) return null;

    // Combine indices and commodities for a full ticker
    const items = [
        ...Object.entries(data.indices_globais),
        ...Object.entries(data.commodities || {})
    ].map(([ticker, data]) => ({
        ticker,
        ...data,
        config: INDICES_CONFIG[ticker] || { name: ticker }
    }));

    // Duplicate items for seamless infinite scroll
    const tickerItems = [...items, ...items];

    return (
        <div className="w-full bg-black border-y border-slate-800 overflow-hidden relative h-10 flex items-center">
            {/* Gradient Masks for Fade Effect */}
            <div className="absolute left-0 top-0 bottom-0 w-16 bg-gradient-to-r from-slate-950 to-transparent z-10 pointer-events-none" />
            <div className="absolute right-0 top-0 bottom-0 w-16 bg-gradient-to-l from-slate-950 to-transparent z-10 pointer-events-none" />

            <div className="flex animate-marquee whitespace-nowrap hover:pause-animation">
                {tickerItems.map((item, idx) => {
                    const isPositive = item.var_pct > 0;
                    const isNegative = item.var_pct < 0;
                    const colorClass = isPositive ? 'text-emerald-400' : isNegative ? 'text-red-500' : 'text-slate-400';

                    return (
                        <div key={`${item.ticker}-${idx}`} className="flex items-center gap-3 px-6 border-r border-slate-800/50">
                            <span className="font-bold text-slate-300 text-sm">{item.config.name}</span>

                            <div className={`flex items-center gap-1 font-mono font-bold text-sm ${colorClass}`}>
                                {isPositive ? <TrendingUp className="w-3 h-3" /> : isNegative ? <TrendingDown className="w-3 h-3" /> : <Minus className="w-3 h-3" />}
                                <span>{item.valor.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
                            </div>

                            <div className={`text-xs font-bold ${colorClass}`}>
                                {item.var_pct > 0 ? '+' : ''}{item.var_pct.toFixed(2)}%
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
