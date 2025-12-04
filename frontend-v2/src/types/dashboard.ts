export interface IndiceData {
    valor: number;
    var: number;
    var_pct: number;
}

export interface BlueChip {
    valor: number;
    var: number;
    var_pct: number;
}

export interface Commodity {
    valor: number;
    var: number;
    var_pct: number;
}

export interface Taxa {
    valor: number;
    var: number;
    var_pct: number;
}

export interface CalendarEvent {
    time: string;
    currency: string;
    impact: number;
    event: string;
    actual?: string;
    forecast?: string;
    previous?: string;
}

export interface Breadth {
    up: number;
    down: number;
    neutral: number;
    signal: string;
    confidence: number;
}

export interface Basis {
    value: number;
    interpretation: string;
}

export interface SentimentComparison {
    spx_signal: string;
    win_signal: string;
    divergence: boolean;
    status: string;
}

export interface SignalHistoryItem {
    time: string;
    signal: string;
}

export interface DashboardData {
    formatted_time: string;
    timestamp: string;
    indices_globais: Record<string, IndiceData>;
    commodities: Record<string, Commodity>;
    blue_chips: Record<string, BlueChip>;
    taxas: Record<string, Taxa>;
    calendar: CalendarEvent[];
    breadth?: Breadth;
    basis?: Basis;
    sentiment_comparison?: SentimentComparison;
    signal_history?: SignalHistoryItem[];
}

export interface WebSocketMessage {
    type: string;
    data: DashboardData;
    timestamp: string;
}
