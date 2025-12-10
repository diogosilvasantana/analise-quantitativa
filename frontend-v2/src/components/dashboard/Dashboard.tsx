'use client';

import React, { useState, useCallback } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { DashboardData, WebSocketMessage } from '@/types/dashboard';
import { ErrorBoundary } from '../shared/ErrorBoundary';
import { IndicesPanel } from './IndicesPanel';
import { CommoditiesPanel } from './CommoditiesPanel';
import { IBOVTop10Panel } from './IBOVTop10Panel';
import { TaxesPanel } from './TaxesPanel';
import { AIAnalysisPanel, AIContextCard } from './AIAnalysisPanel';
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

            {/* 3-COLUMN ASSET-CENTRIC LAYOUT (40/40/20) */}
            <div className="grid grid-cols-1 xl:grid-cols-10 gap-6 max-w-[1920px] mx-auto xl:h-[calc(100vh-140px)]">

                {/* === COLUMN 1: WIN (Index) - 40% === */}
                <div className="xl:col-span-4 flex flex-col gap-4 h-full">
                    {/* Header / Termometer */}
                    <div className="flex-none">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-blue-400 font-bold text-lg">WIN (Índice)</span>
                            <div className="h-px bg-blue-900/50 flex-1"></div>
                        </div>
                        <MarketThermometer
                            title="Força WIN"
                            bullPower={winScore.bull_power}
                            bearPower={winScore.bear_power}
                            maxPower={100}
                        />
                    </div>

                    {/* AI Context Card */}
                    <div className="flex-none h-48">
                        <AIContextCard
                            title="Contexto IA (WIN)"
                            assetType="WIN"
                            context={dashboardData.ai_analysis?.win_context}
                        />
                    </div>

                    {/* Quant Flow (Full Height remaining) */}
                    <div className="flex-1 min-h-0">
                        <QuantPanel data={dashboardData} asset="WIN" />
                    </div>
                </div>


                {/* === COLUMN 2: WDO (Dollar) - 40% === */}
                <div className="xl:col-span-4 flex flex-col gap-4 h-full">
                    {/* Header / Termometer */}
                    <div className="flex-none">
                        <div className="flex items-center gap-2 mb-2">
                            <span className="text-green-400 font-bold text-lg">WDO (Dólar)</span>
                            <div className="h-px bg-green-900/50 flex-1"></div>
                        </div>
                        <MarketThermometer
                            title="Força WDO"
                            bullPower={wdoScore.bull_power}
                            bearPower={wdoScore.bear_power}
                            maxPower={100}
                        />
                    </div>

                    {/* AI Context Card */}
                    <div className="flex-none h-48">
                        <AIContextCard
                            title="Contexto IA (WDO)"
                            assetType="WDO"
                            context={dashboardData.ai_analysis?.wdo_context}
                        />
                    </div>

                    {/* Quant Flow (Full Height remaining) */}
                    <div className="flex-1 min-h-0">
                        <QuantPanel data={dashboardData} asset="WDO" />
                    </div>
                </div>


                {/* === COLUMN 3: SIDEBAR (Context) - 20% === */}
                <div className="xl:col-span-2 flex flex-col gap-4 h-full xl:overflow-y-auto pr-1">
                    {/* Global Narrative */}
                    <div className="flex-none">
                        <AIAnalysisPanel data={dashboardData.ai_analysis} />
                    </div>

                    {/* Calendar */}
                    <div className="flex-none">
                        <EconomicCalendar data={dashboardData} />
                    </div>

                    {/* Asset Drivers */}
                    <div className="flex-none space-y-4">
                        <IBOVTop10Panel data={dashboardData} />
                        <CommoditiesPanel data={dashboardData} />
                    </div>
                </div>

            </div>

            {/* Footer Ticker */}
            <div className="w-full mt-4 border-t border-slate-800 pt-2 opacity-60 hover:opacity-100 transition-opacity">
                <IndicesPanel data={dashboardData} />
            </div>

        </div>
    );
}
