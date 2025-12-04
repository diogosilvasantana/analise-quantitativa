import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip } from 'recharts';

// --- Translation Helper ---
const signalMap = {
    "STRONG_BUY": "COMPRA FORTE 🐂",
    "STRONG_SELL": "VENDA FORTE 🐻",
    "BULLISH_DIVERGENCE": "DIVERGÊNCIA ALTISTA 💎",
    "BEARISH_DIVERGENCE": "DIVERGÊNCIA BAIXISTA ⚠️",
    "BUY": "COMPRA 📈",
    "SELL": "VENDA 📉",
    "NEUTRAL": "NEUTRO 😐"
};

const getSignalLabel = (key) => signalMap[key] || key;

// --- Sub-Components ---

const BasisGaugeCircular = ({ value }) => {
    // Normalize value (-2000 to 2000) to (0 to 100)
    const clamped = Math.max(-2000, Math.min(2000, value));
    const percent = ((clamped + 2000) / 4000) * 100;

    // Gauge Data (Background and Value)
    const data = [
        { name: 'Valor', value: percent },
        { name: 'Resto', value: 100 - percent }
    ];

    // Color Logic
    let color = '#888';
    if (value > 500) color = '#00ff88'; // Premium
    else if (value < -500) color = '#ff3333'; // Discount
    else color = '#ffd700'; // Flat

    return (
        <div style={{ width: '100%', height: 120, position: 'relative' }}>
            <ResponsiveContainer>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="70%"
                        startAngle={180}
                        endAngle={0}
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={0}
                        dataKey="value"
                        stroke="none"
                    >
                        <Cell key="val" fill={color} />
                        <Cell key="rest" fill="#333" />
                    </Pie>
                    <Tooltip
                        contentStyle={{ background: '#1a1f3a', border: '1px solid #333', borderRadius: '4px' }}
                        itemStyle={{ color: '#fff' }}
                        formatter={(value, name) => [name === 'Valor' ? `${value.toFixed(0)}%` : value, name]}
                    />
                </PieChart>
            </ResponsiveContainer>
            <div style={{ position: 'absolute', bottom: 10, width: '100%', textAlign: 'center', color: '#fff', fontWeight: 'bold' }}>
                {value > 0 ? '+' : ''}{value.toFixed(0)}
            </div>
            <div style={{ position: 'absolute', bottom: -5, width: '100%', textAlign: 'center', fontSize: '0.7em', color: '#aaa' }}>
                BASIS (FUTURO)
            </div>
        </div>
    );
};

const BreadthDonutChart = ({ up, down, neutral }) => {
    const data = [
        { name: 'Alta', value: up, color: '#00ff88' },
        { name: 'Baixa', value: down, color: '#ff3333' },
        { name: 'Neutro', value: neutral, color: '#888' }
    ];

    return (
        <div style={{ width: '100%', height: 120 }}>
            <ResponsiveContainer>
                <PieChart>
                    <Pie
                        data={data}
                        cx="50%"
                        cy="50%"
                        innerRadius={35}
                        outerRadius={50}
                        paddingAngle={5}
                        dataKey="value"
                        stroke="none"
                    >
                        {data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                    </Pie>
                    <Tooltip
                        contentStyle={{ background: '#1a1f3a', border: '1px solid #333', borderRadius: '4px' }}
                        itemStyle={{ color: '#fff' }}
                    />
                </PieChart>
            </ResponsiveContainer>
            <div style={{ textAlign: 'center', marginTop: -10, fontSize: '0.8em', color: '#aaa' }}>
                {up}⬆ {down}⬇
            </div>
        </div>
    );
};

const SignalTimelineChart = ({ data }) => {
    if (!data || data.length === 0) return null;

    // Map signals to numeric values for chart
    const signalToVal = (s) => {
        if (s.includes('STRONG_BUY')) return 2;
        if (s.includes('BUY')) return 1;
        if (s.includes('SELL')) return -1;
        if (s.includes('STRONG_SELL')) return -2;
        return 0;
    };

    const chartData = data.map(d => ({
        time: d.time,
        val: signalToVal(d.signal),
        signal: d.signal,
        label: getSignalLabel(d.signal) // Add translated label
    }));

    return (
        <div style={{ width: '100%', height: 100, marginTop: 20 }}>
            <h4 style={{ fontSize: '0.8em', color: '#666', marginBottom: 5 }}>Linha do Tempo (Sinais)</h4>
            <ResponsiveContainer>
                <LineChart data={chartData}>
                    <XAxis dataKey="time" hide />
                    <YAxis domain={[-2.5, 2.5]} hide />
                    <Line
                        type="stepAfter"
                        dataKey="val"
                        stroke="#00ccff"
                        strokeWidth={2}
                        dot={{ r: 3, fill: '#00ccff' }}
                        activeDot={{ r: 5, fill: '#fff' }}
                    />
                    <Tooltip
                        contentStyle={{ background: '#1a1f3a', border: 'none' }}
                        labelStyle={{ color: '#888' }}
                        formatter={(value, name, props) => [props.payload.label, 'Sinal']}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

const ComparisonWithAlert = ({ sentiment }) => {
    if (!sentiment) return null;
    const { spx_signal, win_signal, divergence, status } = sentiment;

    return (
        <div className={`comparison-pro ${divergence ? 'divergence-alert' : ''}`}>
            <div className="comp-header">Contexto Global</div>
            <div className="comp-grid">
                <div className="comp-col">
                    <span className="comp-title">S&P 500</span>
                    <span className={`comp-val ${spx_signal.includes('BUY') ? 'bullish' : spx_signal.includes('SELL') ? 'bearish' : ''}`}>
                        {getSignalLabel(spx_signal)}
                    </span>
                </div>
                <div className="comp-vs">vs</div>
                <div className="comp-col">
                    <span className="comp-title">WIN</span>
                    <span className={`comp-val ${win_signal.includes('BUY') ? 'bullish' : win_signal.includes('SELL') ? 'bearish' : ''}`}>
                        {getSignalLabel(win_signal)}
                    </span>
                </div>
            </div>
            <div className={`comp-status ${divergence ? 'warning' : 'success'}`}>
                {status}
            </div>
        </div>
    );
};

// --- Main Component ---

export function MarketSentimentPanelPRO({ data }) {
    if (!data) return null;

    const { basis, breadth, sentiment_comparison, signal_history } = data;

    const mainSignal = breadth ? breadth.signal : "NEUTRAL";
    const confidence = breadth ? breadth.confidence : 0;

    return (
        <div className="sentiment-container pro">
            {/* 1. Hero Signal */}
            <div className="signal-hero">
                <div className={`signal-value ${mainSignal}`}>
                    {getSignalLabel(mainSignal)}
                </div>
                <div className="signal-confidence">
                    Confiança: <span style={{ color: confidence > 70 ? '#00ff88' : '#ffcc00' }}>{confidence.toFixed(0)}%</span>
                </div>
            </div>

            {/* 2. Critical Alerts */}
            {sentiment_comparison && sentiment_comparison.divergence && (
                <div className="alert-banner warning-animated">
                    ⚠️ DIVERGÊNCIA INTERNACIONAL DETECTADA
                </div>
            )}

            {/* 3. Metrics Grid */}
            <div className="metrics-grid">
                {/* Basis Gauge */}
                {basis && (
                    <div className="metric-card basis-pro">
                        <BasisGaugeCircular value={basis.value} />
                    </div>
                )}

                {/* Breadth Donut */}
                {breadth && (
                    <div className="metric-card breadth-pro">
                        <BreadthDonutChart
                            up={breadth.up}
                            down={breadth.down}
                            neutral={breadth.neutral}
                        />
                    </div>
                )}

                {/* Comparison */}
                {sentiment_comparison && (
                    <div className="metric-card comparison-pro-card">
                        <ComparisonWithAlert sentiment={sentiment_comparison} />
                    </div>
                )}
            </div>

            {/* 4. Timeline */}
            <div className="timeline-pro">
                <SignalTimelineChart data={signal_history} />
            </div>
        </div>
    );
}
