import React from 'react';

export function MarketSentimentPanel({ data }) {
    if (!data) return null;

    const { basis, breadth, sentiment_comparison, signal_history } = data;

    // Translation Maps
    const basisMap = {
        "PREMIUM_HIGH": "Otimismo Exagerado 🚀",
        "PREMIUM_NORMAL": "Prêmio Normal ✅",
        "FLAT": "Indecisão 😐",
        "DISCOUNT": "Desconto (Backwardation) 📉",
        "DISCOUNT_HIGH": "Pessimismo Extremo 💀",
        "LEGACY": "Dados Antigos",
        "NEUTRAL": "Neutro"
    };

    const signalMap = {
        "STRONG_BUY": "Compra Forte 🐂",
        "STRONG_SELL": "Venda Forte 🐻",
        "BULLISH_DIVERGENCE": "Divergência Altista 💎",
        "BEARISH_DIVERGENCE": "Divergência Baixista ⚠️",
        "BUY": "Compra 📈",
        "SELL": "Venda 📉",
        "NEUTRAL": "Neutro 😐"
    };

    const getBasisLabel = (key) => basisMap[key] || key;
    const getSignalLabel = (key) => signalMap[key] || key;

    // Helper for Basis Meter Position (Range: -2000 to +2000)
    const getBasisPercent = (val) => {
        const clamped = Math.max(-2000, Math.min(2000, val));
        return ((clamped + 2000) / 4000) * 100;
    };

    return (
        <div className="panel sentiment-panel premium-glass">
            <div className="panel-header">
                <h2>🧠 Inteligência de Mercado</h2>
            </div>

            <div className="sentiment-grid">

                {/* 1. International Context (SPX vs WIN) */}
                {sentiment_comparison && (
                    <div className="sentiment-card comparison-card">
                        <h3>Contexto Internacional 🌎</h3>
                        <div className="comparison-row">
                            <div className="comp-item">
                                <span className="comp-label">S&P 500</span>
                                <span className={`comp-val ${sentiment_comparison.spx_signal.includes('BUY') ? 'bullish-text' : 'bearish-text'}`}>
                                    {getSignalLabel(sentiment_comparison.spx_signal)}
                                </span>
                            </div>
                            <div className="comp-divider">vs</div>
                            <div className="comp-item">
                                <span className="comp-label">WIN (Brasil)</span>
                                <span className={`comp-val ${sentiment_comparison.win_signal.includes('BUY') ? 'bullish-text' : 'bearish-text'}`}>
                                    {getSignalLabel(sentiment_comparison.win_signal)}
                                </span>
                            </div>
                        </div>
                        <div className={`status-badge ${sentiment_comparison.divergence ? 'warning' : 'success'}`}>
                            {sentiment_comparison.status}
                        </div>
                    </div>
                )}

                {/* 2. Basis Section */}
                {basis && (
                    <div className="sentiment-card basis-card">
                        <div className="card-header">
                            <h3>Basis (Futuro vs À Vista)</h3>
                            <span className="basis-value-small">{basis.value > 0 ? '+' : ''}{basis.value.toFixed(0)} pts</span>
                        </div>

                        <div className="gauge-container">
                            <div className="gauge-bar">
                                <div className="gauge-fill" style={{ width: `${getBasisPercent(basis.value)}%` }}></div>
                                <div className="gauge-marker" style={{ left: `${getBasisPercent(basis.value)}%` }}></div>
                            </div>
                            <div className="gauge-labels">
                                <span>Desconto</span>
                                <span>Zero</span>
                                <span>Prêmio</span>
                            </div>
                        </div>

                        <div className={`metric-label-large ${basis.interpretation.includes('PREMIUM') ? 'bullish-text' : 'bearish-text'}`}>
                            {getBasisLabel(basis.interpretation)}
                        </div>
                    </div>
                )}

                {/* 3. Breadth Section */}
                {breadth && (
                    <div className="sentiment-card breadth-card">
                        <h3>Força do Movimento (Top 10)</h3>

                        <div className="power-meter">
                            <div className="power-segment up" style={{ width: `${(breadth.up / 10) * 100}%` }}></div>
                            <div className="power-segment down" style={{ width: `${(breadth.down / 10) * 100}%` }}></div>
                        </div>

                        <div className="breadth-stats">
                            <div className="stat-item up">
                                <span className="stat-val">{breadth.up}</span>
                                <span className="stat-label">Altas</span>
                            </div>
                            <div className="stat-item neutral">
                                <span className="stat-val">{breadth.neutral}</span>
                                <span className="stat-label">Neutras</span>
                            </div>
                            <div className="stat-item down">
                                <span className="stat-val">{breadth.down}</span>
                                <span className="stat-label">Baixas</span>
                            </div>
                        </div>

                        {breadth.signal !== 'NEUTRAL' && (
                            <div className={`signal-box ${breadth.signal.includes('BEARISH') || breadth.signal.includes('SELL') ? 'bearish-glow' : 'bullish-glow'}`}>
                                {getSignalLabel(breadth.signal)}
                            </div>
                        )}

                        {/* Confidence Bar */}
                        <div className="confidence-container">
                            <div className="conf-header">
                                <span>Confiança do Sinal</span>
                                <span>{breadth.confidence.toFixed(0)}%</span>
                            </div>
                            <div className="conf-bar-bg">
                                <div className="conf-bar-fill" style={{ width: `${breadth.confidence}%` }}></div>
                            </div>
                        </div>
                    </div>
                )}

                {/* 4. Signal Timeline */}
                {signal_history && signal_history.length > 0 && (
                    <div className="sentiment-card timeline-card">
                        <h3>Últimos Sinais ⏳</h3>
                        <div className="timeline-list">
                            {signal_history.slice().reverse().map((item, idx) => (
                                <div key={idx} className="timeline-item">
                                    <span className="time">{item.time}</span>
                                    <span className={`signal ${item.signal.includes('BUY') ? 'bullish-text' : 'bearish-text'}`}>
                                        {getSignalLabel(item.signal)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
