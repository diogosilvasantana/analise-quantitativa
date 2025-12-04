import React from 'react';

export function MarketMood({ data }) {
    // Debug: Check if data exists
    if (!data) return null;

    // Fallback if intelligence is missing or empty
    if (!data.intelligence || Object.keys(data.intelligence).length === 0) {
        return (
            <div className="panel-section market-mood-panel">
                <h3>🧠 Inteligência de Mercado</h3>
                <div className="loading-message" style={{ padding: '20px', fontSize: '0.9em' }}>
                    ⏳ Carregando dados de IA...
                </div>
            </div>
        );
    }

    const { risk_mode, sentiments, sectors } = data.intelligence;

    // Safety check for properties
    if (!risk_mode || !sentiments || !sectors) {
        return (
            <div className="panel-section market-mood-panel">
                <h3>🧠 Inteligência de Mercado</h3>
                <div className="loading-message" style={{ padding: '20px', fontSize: '0.9em' }}>
                    ⚠️ Dados incompletos. Aguardando atualização...
                </div>
            </div>
        );
    }

    const getRiskColor = (mode) => {
        if (mode === "RISK ON") return "#00ff88"; // Green
        if (mode === "RISK OFF") return "#ff4444"; // Red
        return "#888888"; // Gray
    };

    const getSentimentColor = (sentiment) => {
        if (sentiment.includes("BUY")) return "#00ff88";
        if (sentiment.includes("SELL")) return "#ff4444";
        return "#888888";
    };

    return (
        <div className="panel-section market-mood-panel">
            <h3>🧠 Inteligência de Mercado</h3>

            {/* Risk Clock (Main Gauge) */}
            <div className="risk-clock" style={{ borderColor: getRiskColor(risk_mode) }}>
                <div className="risk-label">MODO DE RISCO</div>
                <div className="risk-value" style={{ color: getRiskColor(risk_mode) }}>
                    {risk_mode}
                </div>
            </div>

            {/* Sentiments (Mini Cards) */}
            <div className="sentiment-grid">
                {Object.entries(sentiments).map(([asset, signal]) => (
                    <div key={asset} className="sentiment-card">
                        <span className="asset-name">{asset}</span>
                        <span className="signal-value" style={{ color: getSentimentColor(signal) }}>
                            {signal.replace("_", " ")}
                        </span>
                    </div>
                ))}
            </div>

            {/* Sectors (Mini Heatmap) */}
            <div className="sectors-list">
                <h4>Setores EUA</h4>
                {Object.entries(sectors).map(([sector, change]) => (
                    <div key={sector} className="sector-row">
                        <span>{sector}</span>
                        <span style={{ color: change >= 0 ? '#00ff88' : '#ff4444' }}>
                            {change > 0 ? '+' : ''}{change.toFixed(2)}%
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
