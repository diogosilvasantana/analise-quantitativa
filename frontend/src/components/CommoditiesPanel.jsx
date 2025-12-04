import React from 'react';

export function CommoditiesPanel({ data }) {
    if (!data || !data.commodities) {
        return null;
    }

    const COMMODITIES_NAMES = {
        "BRENT": "Petróleo Brent",
        "OURO": "Ouro (Gold)",
        "COBRE": "Cobre",
        "MINERIO_FERRO": "Minério de Ferro"
    };

    const renderCommodityCard = (ticker, commodity) => (
        <div key={ticker} className={`card ${commodity.var >= 0 ? 'positive' : 'negative'}`}>
            <div className="card-header">
                <h4>{COMMODITIES_NAMES[ticker] || ticker}</h4>
                <span className="ticker">{ticker}</span>
            </div>
            <div className="price">{commodity.valor.toFixed(2)}</div>
            <div className="variation">
                {commodity.var >= 0 ? '📈' : '📉'} {commodity.var_pct.toFixed(2)}%
            </div>
        </div>
    );

    return (
        <div className="panel-section">
            <h3>Commodities 🛢️</h3>
            <div className="grid">
                {Object.entries(data.commodities).map(([name, commodity]) =>
                    commodity ? renderCommodityCard(name, commodity) : null
                )}
            </div>
        </div>
    );
}
