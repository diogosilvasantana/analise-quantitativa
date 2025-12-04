import React from 'react';

export function IBOVTop10Panel({ data }) {
    if (!data || !data.blue_chips) {
        return null;
    }

    const ASSET_NAMES = {
        "VALE3": "Vale",
        "PETR4": "Petrobras",
        "ITUB4": "Itaú Unibanco",
        "BBDC4": "Bradesco",
        "BBAS3": "Banco do Brasil",
        "WEGE3": "WEG",
        "SBSP3": "Sabesp",
        "RENT3": "Localiza",
        "LREN3": "Lojas Renner",
        "B3SA3": "B3",
        "PETR3": "Petrobras ON",
        "ITSA4": "Itaúsa",
        "BPAC11": "BTG Pactual"
    };

    const renderBlueChipCard = (ticker, blueChip) => (
        <div key={ticker} className={`card ${blueChip.var >= 0 ? 'positive' : 'negative'}`}>
            <div className="card-header">
                <h4>{ASSET_NAMES[ticker] || ticker}</h4>
                <span className="ticker">{ticker}</span>
            </div>
            <div className="price">{blueChip.valor.toFixed(2)}</div>
            <div className="variation">
                {blueChip.var >= 0 ? '📈' : '📉'} {blueChip.var_pct.toFixed(2)}%
            </div>
        </div>
    );

    return (
        <div className="panel-section">
            <h3>IBOV Top 10 Ações 📊</h3>
            <div className="grid">
                {Object.entries(data.blue_chips).map(([name, blueChip]) =>
                    blueChip ? renderBlueChipCard(name, blueChip) : null
                )}
            </div>
        </div>
    );
}
