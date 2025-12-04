'use client';

import React from 'react';
import { Card } from '@/components/ui/card';
import { DashboardData } from '@/types/dashboard';
import { cn } from '@/lib/utils';
import { Calendar as CalendarIcon } from 'lucide-react';

interface EconomicCalendarProps {
    data: DashboardData;
}

export function EconomicCalendar({ data }: EconomicCalendarProps) {
    if (!data?.calendar || data.calendar.length === 0) return null;

    return (
        <Card className="border-slate-700 bg-slate-800/30 p-6">
            <h2 className="text-lg font-bold text-slate-200 mb-4 flex items-center gap-2">
                <CalendarIcon className="w-5 h-5 text-purple-400" />
                Calendário Econômico
            </h2>
            <div className="overflow-x-auto">
                <table className="w-full text-sm text-left">
                    <thead className="text-xs text-slate-400 uppercase bg-slate-900/50">
                        <tr>
                            <th className="px-4 py-3">Hora</th>
                            <th className="px-4 py-3">País</th>
                            <th className="px-4 py-3">Evento</th>
                            <th className="px-4 py-3">Impacto</th>
                            <th className="px-4 py-3">Atual</th>
                            <th className="px-4 py-3">Previsto</th>
                            <th className="px-4 py-3">Anterior</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800">
                        {data.calendar.map((event, idx) => (
                            <tr key={idx} className="hover:bg-slate-800/50 transition-colors">
                                <td className="px-4 py-3 font-mono text-slate-300">{event.time}</td>
                                <td className="px-4 py-3 font-bold text-slate-300">{event.currency}</td>
                                <td className="px-4 py-3 text-slate-300">{event.event}</td>
                                <td className="px-4 py-3">
                                    <div className="flex gap-0.5">
                                        {[...Array(3)].map((_, i) => (
                                            <div
                                                key={i}
                                                className={cn(
                                                    'w-2 h-2 rounded-full',
                                                    i < event.impact
                                                        ? event.impact === 3
                                                            ? 'bg-red-500'
                                                            : event.impact === 2
                                                                ? 'bg-orange-500'
                                                                : 'bg-yellow-500'
                                                        : 'bg-slate-700'
                                                )}
                                            />
                                        ))}
                                    </div>
                                </td>
                                <td className="px-4 py-3 font-mono font-bold text-slate-200">{event.actual || '-'}</td>
                                <td className="px-4 py-3 font-mono text-slate-400">{event.forecast || '-'}</td>
                                <td className="px-4 py-3 font-mono text-slate-500">{event.previous || '-'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </Card>
    );
}
