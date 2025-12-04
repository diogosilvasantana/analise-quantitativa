'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';
import { Package, TrendingUp, TrendingDown } from 'lucide-react';

interface CommoditiesPanelProps {
    data: DashboardData;
}

export function CommoditiesPanel({ data }: CommoditiesPanelProps) {
    if (!data?.commodities) return null;

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Package className="w-5 h-5 text-yellow-400" />
                Commodities
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(data.commodities).map(([ticker, commodity]) => (
                    commodity && (
                        <div
                            key={ticker}
                            className={cn(
                                'p-4 rounded-lg border transition-all hover:border-slate-600',
                                commodity.var >= 0
                                    ? 'border-emerald-500/30 bg-emerald-950/20'
                                    : 'border-red-500/30 bg-red-950/20'
                            )}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <h3 className="text-sm font-semibold text-slate-300">{ticker}</h3>
                            </div>
                            <div className="text-lg font-bold text-slate-100 mb-1 font-mono">
                                {commodity.valor.toFixed(2)}
                            </div>
                            <div
                                className={cn(
                                    'text-sm font-semibold flex items-center gap-1',
                                    commodity.var >= 0 ? 'text-emerald-400' : 'text-red-400'
                                )}
                            >
                                {commodity.var >= 0 ? <TrendingUp className="w-4 h-4" /> : <TrendingDown className="w-4 h-4" />}
                                {commodity.var_pct.toFixed(2)}%
                            </div>
                        </div>
                    )
                ))}
            </div>
        </Card>
    );
}
