import React from 'react';

export function IndicesPanel({ data }) {
    if (!data || !data.indices_globais) {
        return null;
    }

    const INDICES_NAMES = {
        "SP500": "S&P 500",
        "NASDAQ": "Nasdaq 100",
        "DOW_JONES": "Dow Jones",
        "DXY": "Dólar Index",
        "DAX40": "DAX 40 (Alemanha)",
        "US10Y": "Treasury 10Y",
        "EWZ": "EWZ (Brasil ETF)"
    };

    const renderIndiceCard = (ticker, indice) => (
        <div key={ticker} className={`card ${indice.var >= 0 ? 'positive' : 'negative'}`}>
            <div className="card-header">
                <h4>{INDICES_NAMES[ticker] || ticker}</h4>
                <span className="ticker">{ticker}</span>
            </div>
            <div className="price">{indice.valor.toFixed(2)}</div>
            <div className="variation">
                {indice.var >= 0 ? '📈' : '📉'} {indice.var_pct.toFixed(2)}%
            </div>
        </div>
    );

    return (
        <div className="panel-section">
            <h3>Índices Globais 🌍</h3>
            <div className="grid">
                {Object.entries(data.indices_globais).map(([name, indice]) =>
                    indice ? renderIndiceCard(name, indice) : null
                )}
            </div>
        </div>
    );
}
