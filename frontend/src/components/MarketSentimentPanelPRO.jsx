import React, { useState, useEffect } from 'react';

export function MarketSentimentPanelPRO({ data }) {
    const [statusChanged, setStatusChanged] = useState(false);
    const [animateValues, setAnimateValues] = useState({});

    const { basis, breadth, sentiment_comparison, signal_history } = data || {};

    // Animar quando dados mudam
    useEffect(() => {
        setStatusChanged(true);
        const timer = setTimeout(() => setStatusChanged(false), 1500);
        return () => clearTimeout(timer);
    }, [sentiment_comparison?.status, basis?.value]);

    // Translations
    const basisMap = {
        "PREMIUM_HIGH": "Otimismo Exagerado 🚀",
        "PREMIUM_NORMAL": "Prêmio Normal ✅",
        "FLAT": "Indecisão 😐",
        "DISCOUNT": "Desconto (Backwardation) 📉",
        "DISCOUNT_HIGH": "Pessimismo Extremo 💀",
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

    const isBullish = breadth?.signal?.includes('BUY') || false;
    const isBearish = breadth?.signal?.includes('SELL') || false;
    const hasDivergence = sentiment_comparison?.divergence || false;

    return (
        <div className="sentiment-panel-pro">
            {/* ALERT BANNER (Se houver divergência) */}
            {hasDivergence && (
                <div className="alert-banner alert-divergence">
                    <div className="alert-icon">⚠️</div>
                    <div className="alert-text">
                        DIVERGÊNCIA: {getSignalLabel(sentiment_comparison.spx_signal)} vs {getSignalLabel(sentiment_comparison.win_signal)}
                    </div>
                </div>
            )}

            {/* SIGNAL HERO (Dominante) */}
            {breadth && (
                <div className={`signal-hero ${isBullish ? 'bullish' : isBearish ? 'bearish' : 'neutral'}`}>
                    <div className="signal-text">
                        {getSignalLabel(breadth.signal)}
                    </div>
                    <div className={`signal-confidence ${statusChanged ? 'changed' : ''}`}>
                        Confiança: {breadth.confidence.toFixed(0)}%
                    </div>
                </div>
            )}

            {/* METRICS GRID */}
            <div className="sentiment-grid">

                {/* BASIS CARD */}
                {basis && (
                    <div className="sentiment-card basis-card">
                        <h3>Basis (Futuro vs À Vista)</h3>
                        <div className="basis-value-large">
                            {basis.value > 0 ? '+' : ''}{basis.value.toFixed(0)} pts
                        </div>
                        <div className="gauge-semi-circle">
                            <svg viewBox="0 0 200 100" className="gauge-svg">
                                <path d="M 20 80 A 60 60 0 0 1 180 80" className="gauge-track" />
                                <path
                                    d="M 20 80 A 60 60 0 0 1 180 80"
                                    className="gauge-fill"
                                    style={{ strokeDasharray: `${Math.max(0, Math.min(160, (basis.value + 2000) / 25))} 160` }}
                                />
                            </svg>
                        </div>
                        <div className="metric-label-large">
                            {getBasisLabel(basis.interpretation)}
                        </div>
                    </div>
                )}

                {/* BREADTH CARD */}
                {breadth && (
                    <div className="sentiment-card breadth-card">
                        <h3>Força do Movimento (Top 10)</h3>
                        <div className="breadth-donut">
                            <svg viewBox="0 0 100 100" className="donut-svg">
                                <circle cx="50" cy="50" r="45" className="donut-track" />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    className="donut-segment up"
                                    style={{ strokeDasharray: `${(breadth.up / 10) * 282.7} 282.7` }}
                                />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    className="donut-segment neutral"
                                    style={{
                                        strokeDasharray: `${(breadth.neutral / 10) * 282.7} 282.7`,
                                        strokeDashoffset: `-${(breadth.up / 10) * 282.7}`
                                    }}
                                />
                                <circle
                                    cx="50"
                                    cy="50"
                                    r="45"
                                    className="donut-segment down"
                                    style={{
                                        strokeDasharray: `${(breadth.down / 10) * 282.7} 282.7`,
                                        strokeDashoffset: `-${((breadth.up + breadth.neutral) / 10) * 282.7}`
                                    }}
                                />
                                <text x="50" y="50" className="donut-center">{breadth.up}⬆</text>
                            </svg>
                        </div>
                        <div className="breadth-legend">
                            <div><span className="dot up"></span> {breadth.up} Altas</div>
                            <div><span className="dot neutral"></span> {breadth.neutral} Neutras</div>
                            <div><span className="dot down"></span> {breadth.down} Baixas</div>
                        </div>
                    </div>
                )}

                {/* COMPARISON CARD */}
                {sentiment_comparison && (
                    <div className={`sentiment-card comparison-card ${hasDivergence ? 'divergence-alert' : ''}`}>
                        <h3>SPX vs WIN</h3>
                        <div className="comparison-content">
                            <div className="comp-item">
                                <span className="comp-label">S&P 500</span>
                                <span className={`comp-signal ${sentiment_comparison.spx_signal.includes('BUY') ? 'bullish' : 'bearish'}`}>
                                    {getSignalLabel(sentiment_comparison.spx_signal)}
                                </span>
                            </div>
                            <div className="comp-divider">{hasDivergence ? '⚠️' : '✅'}</div>
                            <div className="comp-item">
                                <span className="comp-label">WIN</span>
                                <span className={`comp-signal ${sentiment_comparison.win_signal.includes('BUY') ? 'bullish' : 'bearish'}`}>
                                    {getSignalLabel(sentiment_comparison.win_signal)}
                                </span>
                            </div>
                        </div>
                        <div className={`status-badge ${sentiment_comparison.status === 'ALINHADO' ? 'success' : 'warning'}`}>
                            {sentiment_comparison.status}
                        </div>
                    </div>
                )}
            </div>

            {/* TIMELINE */}
            {signal_history && signal_history.length > 0 && (
                <div className="sentiment-card timeline-card">
                    <h3>Histórico de Sinais ⏳</h3>
                    <div className="timeline-visual">
                        <svg className="timeline-svg" viewBox={`0 0 ${signal_history.length * 40} 60`}>
                            <line x1="0" y1="30" x2={signal_history.length * 40} y2="30" className="timeline-line" />
                            {signal_history.map((item, idx) => (
                                <g key={idx} transform={`translate(${idx * 40 + 20}, 30)`}>
                                    <circle
                                        r="6"
                                        className={`timeline-dot ${item.signal.includes('BUY') ? 'bullish' : 'bearish'}`}
                                    />
                                    <text y="20" className="timeline-label">{item.time}</text>
                                </g>
                            ))}
                        </svg>
                    </div>
                </div>
            )}
        </div>
    );
}
