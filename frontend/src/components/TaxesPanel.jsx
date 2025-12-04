import React from 'react';

export function TaxesPanel({ data }) {
    if (!data || !data.taxas) {
        return null;
    }

    const renderTaxaCard = (name, taxa) => (
        <div key={name} className={`card ${taxa.var >= 0 ? 'positive' : 'negative'}`}>
            <h4>{name}</h4>
            <div className="price">{taxa.valor.toFixed(2)}</div>
            <div className="variation">
                {taxa.var >= 0 ? '📈' : '📉'} {taxa.var_pct.toFixed(2)}%
            </div>
        </div>
    );

    return (
        <div className="panel-section">
            <h3>Taxas e Juros 💰</h3>
            <div className="grid">
                {Object.entries(data.taxas).map(([name, taxa]) =>
                    taxa ? renderTaxaCard(name, taxa) : null
                )}
            </div>
        </div>
    );
}
