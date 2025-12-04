'use client';

import React, { useState, useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { DashboardData, WebSocketMessage } from '@/types/dashboard';
import { Header } from '../shared/Header';
import { StatusBar } from '../shared/StatusBar';
import { MarketSentimentPanelPRO } from './MarketSentimentPanelPRO';
import { IndicesPanel } from './IndicesPanel';
import { CommoditiesPanel } from './CommoditiesPanel';
import { IBOVTop10Panel } from './IBOVTop10Panel';
import { TaxesPanel } from './TaxesPanel';
import { EconomicCalendar } from './EconomicCalendar';

export function Dashboard() {
    const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
    const [lastUpdate, setLastUpdate] = useState<string | null>(null);

    const handleWebSocketMessage = useCallback((message: WebSocketMessage) => {
        if (message.type === 'DASHBOARD_UPDATE') {
            setDashboardData(message.data);
            if (message.data.formatted_time) {
                setLastUpdate(message.data.formatted_time);
            }
        }
    }, []);

    const { isConnected } = useWebSocket(
        `ws://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000/ws/dashboard`,
        handleWebSocketMessage
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
            <Header />
            <StatusBar isConnected={isConnected} lastUpdate={lastUpdate} />

            <main className="container mx-auto px-4 py-8">
                {dashboardData ? (
                    <div className="space-y-6">
                        <MarketSentimentPanelPRO data={dashboardData} />

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <IndicesPanel data={dashboardData} />
                            <CommoditiesPanel data={dashboardData} />
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            <IBOVTop10Panel data={dashboardData} />
                            <TaxesPanel data={dashboardData} />
                        </div>

                        <EconomicCalendar data={dashboardData} />
                    </div>
                ) : (
                    <div className="flex flex-col items-center justify-center h-96 bg-slate-900/50 rounded-lg border border-slate-800">
                        <p className="text-slate-400 text-lg">⏳ Aguardando dados do backend...</p>
                        <p className="text-slate-500 text-sm mt-2">Verifique se o backend e o MT5 estão rodando.</p>
                    </div>
                )}
            </main>
        </div>
    );
}
