'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';
import { Banknote } from 'lucide-react';

interface TaxesPanelProps {
    data: DashboardData;
}

export function TaxesPanel({ data }: TaxesPanelProps) {
    if (!data?.taxas) return null;

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Banknote className="w-5 h-5 text-green-400" />
                Taxas & Moedas
            </h2>
            <div className="space-y-3">
                {Object.entries(data.taxas).map(([ticker, taxa]) => (
                    taxa && (
                        <div
                            key={ticker}
                            className="flex items-center justify-between p-3 rounded bg-slate-900/50 border border-slate-800 hover:border-slate-600 transition-colors"
                        >
                            <span className="text-sm font-semibold text-slate-300">{ticker}</span>
                            <div className="text-right">
                                <div className="text-sm font-bold text-slate-100 font-mono">
                                    {taxa.valor.toFixed(3)}
                                </div>
                                <div
                                    className={cn(
                                        'text-xs',
                                        taxa.var >= 0 ? 'text-emerald-400' : 'text-red-400'
                                    )}
                                >
                                    {taxa.var_pct.toFixed(2)}%
                                </div>
                            </div>
                        </div>
                    )
                ))}
            </div>
        </Card>
    );
}
