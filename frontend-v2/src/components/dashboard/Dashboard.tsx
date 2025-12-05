'use client';

import React, { useState, useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { DashboardData, WebSocketMessage } from '@/types/dashboard';
import { ErrorBoundary } from '../shared/ErrorBoundary';
import { IndicesPanel } from './IndicesPanel';
import { CommoditiesPanel } from './CommoditiesPanel';
import { IBOVTop10Panel } from './IBOVTop10Panel';
import { TaxesPanel } from './TaxesPanel';
import { AIAnalysisPanel } from './AIAnalysisPanel';
import QuantPanel from './QuantPanel';
import MarketThermometer from './MarketThermometer';
import { EconomicCalendar } from './EconomicCalendar';
import { Activity, Clock, ShieldCheck } from 'lucide-react';

export default function Dashboard() {
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

    const { isConnected, reconnect } = useWebSocket(
        `ws://${typeof window !== 'undefined' ? window.location.hostname : 'localhost'}:8000/ws/dashboard`,
        handleWebSocketMessage
    );

    // Extract Scores for Thermometers
    const winScore = dashboardData?.quant_dashboard?.score?.WIN || { bull_power: 0, bear_power: 0 };
    const wdoScore = dashboardData?.quant_dashboard?.score?.WDO || { bull_power: 0, bear_power: 0 };

    if (!dashboardData) {
        return (
            <div className="flex items-center justify-center h-screen bg-slate-950 text-slate-400">
                <div className="text-center space-y-4">
                    <div className="animate-spin w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
                    <p>Carregando dados do mercado...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-slate-950 text-slate-200 p-4 md:p-6 font-sans">
            {/* Header */}
            <header className="flex flex-col md:flex-row items-center justify-between mb-6 gap-4 border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                    <div className="bg-blue-600 p-2 rounded-lg shadow-lg shadow-blue-900/20">
                        <Activity className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                            AI Trader Pro
                        </h1>
                        <p className="text-xs text-slate-500 font-medium tracking-wide">QUANTITATIVE INTELLIGENCE</p>
                    </div>
                </div>

                <div className="flex items-center gap-4 bg-slate-900/50 p-2 rounded-full border border-slate-800">
                    <a href="/admin/auditor" className="flex items-center gap-2 px-3 border-r border-slate-800 hover:text-indigo-400 transition-colors" title="AI Auditor">
                        <ShieldCheck className="w-4 h-4 text-slate-400" />
                    </a>
                    <div className="flex items-center gap-2 px-3 border-r border-slate-800">
                        <Clock className="w-4 h-4 text-slate-400" />
                        <span className="text-sm font-mono text-slate-300">{dashboardData.formatted_time}</span>
                    </div>
                    <div className="flex items-center gap-2 px-3">
                        <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-red-500'}`} />
                        <span className="text-xs font-medium text-slate-400 uppercase tracking-wider">
                            {isConnected ? 'Conectado' : 'Desconectado'}
                        </span>
                    </div>
                </div>
            </header>

            {/* Main Grid */}
            <div className="grid grid-cols-1 gap-6 max-w-[1920px] mx-auto">

                {/* Top Row: Global Indices Ticker */}
                <div className="w-full">
                    <IndicesPanel data={dashboardData} />
                </div>

                {/* Second Row: Market Thermometers (Gauge) */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <MarketThermometer
                        title="Termômetro WIN (Índice)"
                        bullPower={winScore.bull_power}
                        bearPower={winScore.bear_power}
                        maxPower={100}
                    />
                    <MarketThermometer
                        title="Termômetro WDO (Dólar)"
                        bullPower={wdoScore.bull_power}
                        bearPower={wdoScore.bear_power}
                        maxPower={100}
                    />
                </div>

                {/* Third Row: Quant Flow + Bar Charts */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <QuantPanel data={dashboardData} />
                    <IBOVTop10Panel data={dashboardData} />
                    <CommoditiesPanel data={dashboardData} />
                </div>

                {/* Bottom Row: Taxes + AI Analysis + Calendar */}
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <TaxesPanel data={dashboardData} />
                    <AIAnalysisPanel data={dashboardData.ai_analysis} />
                    <EconomicCalendar data={dashboardData} />
                </div>
            </div>
        </div>
    );
}
