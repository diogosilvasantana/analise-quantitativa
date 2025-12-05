import React, { useState } from 'react';
import { useWebSocket } from './hooks/useWebSocket';
import { IndicesPanel } from './components/IndicesPanel';
import { CommoditiesPanel } from './components/CommoditiesPanel';
import { IBOVTop10Panel } from './components/IBOVTop10Panel';
import { TaxesPanel } from './components/TaxesPanel';
import { EconomicCalendar } from './components/EconomicCalendar';
import { MarketSentimentPanelPRO } from './components/MarketSentimentPanelPRO';
import AIAnalysisPanel from './components/AIAnalysisPanel';
import './index.css'; // Importa o CSS global

function App() {
    const [dashboardData, setDashboardData] = useState(null);
    const [lastUpdate, setLastUpdate] = useState(null);

    const handleWebSocketMessage = React.useCallback((message) => {
        if (message.type === 'DASHBOARD_UPDATE') {
            setDashboardData(message.data);
            // Use pre-formatted time from backend (Foolproof)
            if (message.data.formatted_time) {
                setLastUpdate(message.data.formatted_time);
            } else {
                // Fallback
                const date = new Date(message.timestamp);
                setLastUpdate(date.toLocaleTimeString('pt-BR', { timeZone: 'America/Sao_Paulo' }));
            }
        }
    }, []);

    const { isConnected } = useWebSocket(
        `ws://${window.location.hostname}:8000/ws/dashboard`, // Conecta ao WebSocket do backend
        handleWebSocketMessage
    );

    return (
        <div className="app-container">
            <header className="app-header">
                <h1>AI-TRADER-PRO Dashboard</h1>
                <div className="status-bar">
                    Status: {isConnected ? '✅ Conectado' : '❌ Desconectado'} |
                    Última atualização: {lastUpdate || 'N/A'}
                </div>
            </header>

            <main className="dashboard-grid">
                {dashboardData ? (
                    <>
                        <div className="col-span-full">
                            <AIAnalysisPanel />
                        </div>
                        <MarketSentimentPanelPRO data={dashboardData} />
                        <IndicesPanel data={dashboardData} />
                        <CommoditiesPanel data={dashboardData} />
                        <IBOVTop10Panel data={dashboardData} />
                        <TaxesPanel data={dashboardData} />
                        <EconomicCalendar data={dashboardData} />
                    </>
                ) : (
                    <div className="loading-message">
                        <p>Aguardando dados do backend...</p>
                        <p>Verifique se o backend e o MT5 estão rodando.</p>
                    </div>
                )}
            </main>
        </div>
    );
}

export default App;
