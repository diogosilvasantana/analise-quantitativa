'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { Package } from 'lucide-react';
import { Bar, BarChart, Cell, ResponsiveContainer, XAxis, YAxis, Tooltip, LabelList } from 'recharts';

interface CommoditiesPanelProps {
    data: DashboardData;
}

export function CommoditiesPanel({ data }: CommoditiesPanelProps) {
    if (!data?.commodities) return null;

    // Transform data for Recharts
    const chartData = Object.entries(data.commodities)
        .map(([ticker, commodity]) => ({
            name: ticker,
            value: commodity.var_pct,
            price: commodity.valor,
            color: commodity.var_pct >= 0 ? '#10b981' : '#ef4444'
        }))
        .sort((a, b) => b.value - a.value);

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-4 h-full">
            <h2 className="text-sm font-bold text-slate-200 mb-4 flex items-center gap-2">
                <Package className="w-4 h-4 text-yellow-400" />
                Commodities (%)
            </h2>
            <div className="h-[200px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart layout="vertical" data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                        <XAxis type="number" hide />
                        <YAxis
                            dataKey="name"
                            type="category"
                            tick={{ fill: '#94a3b8', fontSize: 10 }}
                            width={40}
                            axisLine={false}
                            tickLine={false}
                        />
                        <Tooltip
                            contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                            itemStyle={{ color: '#f8fafc' }}
                            formatter={(value: number) => [`${value.toFixed(2)}%`, 'Variação']}
                            labelStyle={{ color: '#94a3b8' }}
                        />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                            {chartData.map((entry, index) => (
                                <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                            <LabelList dataKey="value" position="right" fill="#94a3b8" fontSize={10} formatter={(val: any) => `${Number(val).toFixed(2)}%`} />
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </div>
        </Card>
    );
}
