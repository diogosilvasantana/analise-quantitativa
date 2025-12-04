'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';
import { BarChart3 } from 'lucide-react';

interface IBOVTop10PanelProps {
    data: DashboardData;
}

export function IBOVTop10Panel({ data }: IBOVTop10PanelProps) {
    if (!data?.blue_chips) return null;

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-400" />
                Top 10 IBOV
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {Object.entries(data.blue_chips).map(([ticker, stock]) => (
                    stock && (
                        <div
                            key={ticker}
                            className={cn(
                                'p-3 rounded-lg border transition-all hover:border-slate-600',
                                stock.var >= 0
                                    ? 'border-emerald-500/30 bg-emerald-950/20'
                                    : 'border-red-500/30 bg-red-950/20'
                            )}
                        >
                            <div className="flex items-center justify-between mb-1">
                                <h3 className="text-sm font-bold text-slate-200">{ticker}</h3>
                                <span
                                    className={cn(
                                        'text-xs font-bold',
                                        stock.var >= 0 ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {stock.var_pct.toFixed(2)}%
                                </span>
                            </div>
                            <div className="text-sm text-slate-400 font-mono">
                                R$ {stock.valor.toFixed(2)}
                            </div>
                        </div>
                    )
                ))}
            </div>
        </Card>
    );
}
