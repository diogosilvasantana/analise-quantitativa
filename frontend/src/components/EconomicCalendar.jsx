import React from 'react';

export function EconomicCalendar({ data }) {
    if (!data || !data.calendar || data.calendar.length === 0) {
        return (
            <div className="panel-section">
                <h3>Calendário Econômico 📅</h3>
                <div className="card">
                    <div style={{ padding: '1rem', textAlign: 'center', color: '#888' }}>
                        Sem eventos de alto impacto restantes para hoje.
                    </div>
                </div>
            </div>
        );
    }

    const renderStars = (count) => {
        // Renderiza estrelas douradas para impacto
        return (
            <span style={{ color: '#FFD700', letterSpacing: '2px' }}>
                {"★".repeat(count)}
            </span>
        );
    };

    return (
        <div className="panel-section">
            <h3>Calendário Econômico 📅</h3>
            <div className="calendar-container">
                <table className="calendar-table">
                    <thead>
                        <tr>
                            <th>Hora</th>
                            <th>País</th>
                            <th>Impacto</th>
                            <th style={{ textAlign: 'left' }}>Evento</th>
                            <th>Atual</th>
                            <th>Proj.</th>
                            <th>Prévio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {data.calendar.map((event, index) => {
                            // Logic to check if event passed
                            const now = new Date();
                            const [hours, minutes] = event.time.split(':');
                            const eventDate = new Date();
                            eventDate.setHours(parseInt(hours), parseInt(minutes), 0);

                            // If event time is > 2 hours ago, consider passed (simple heuristic for today)
                            // Or just check if time < now
                            const isPassed = eventDate < now;
                            const isHighImpact = event.impact >= 3;

                            return (
                                <tr key={index} className={`calendar-row ${isPassed ? 'passed' : ''} ${isHighImpact ? 'high-impact' : ''}`}>
                                    <td className="time">{event.time}</td>
                                    <td className="currency">{event.currency}</td>
                                    <td className="impact">{renderStars(event.impact)}</td>
                                    <td className="event-name">{event.event}</td>
                                    <td className={`actual ${event.actual ? 'highlight' : ''}`}>{event.actual || '-'}</td>
                                    <td className="forecast">{event.forecast || '-'}</td>
                                    <td className="previous">{event.previous || '-'}</td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
