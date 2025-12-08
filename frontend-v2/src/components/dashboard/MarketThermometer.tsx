import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from 'recharts';

interface MarketThermometerProps {
    title: string;
    bullPower: number;
    bearPower: number;
    maxPower?: number;
}

const MarketThermometer: React.FC<MarketThermometerProps> = ({ title, bullPower, bearPower, maxPower = 15 }) => {
    // FIX: Use absolute scores, not net difference
    // The needle should point based on which side is dominant

    const totalPower = bullPower + bearPower;

    // Calculate needle position (0-100%)
    // If only bull power: 100% (far right)
    // If only bear power: 0% (far left)
    // If equal: 50% (center)
    let percentage = 50; // Default center

    if (totalPower > 0) {
        percentage = (bullPower / totalPower) * 100;
    }

    // Gauge Data (Background Arc)
    const data = [
        { name: 'Bearish', value: 1, color: '#ef4444' }, // Red
        { name: 'Neutral', value: 1, color: '#eab308' }, // Yellow
        { name: 'Bullish', value: 1, color: '#22c55e' }, // Green
    ];

    // Needle Rotation (0% = far left/red, 100% = far right/green)
    const needleAngle = 180 - (percentage / 100 * 180);

    return (
        <Card className="bg-slate-900 border-slate-800 relative overflow-hidden">
            <CardHeader className="pb-2 pt-3">
                <CardTitle className="text-sm font-medium text-slate-400 flex items-center justify-center gap-2 uppercase tracking-wider">
                    {title}
                </CardTitle>
            </CardHeader>
            <CardContent className="flex items-center justify-between px-6 pb-4">

                {/* Bear Side */}
                <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/20">
                        <TrendingDown className="w-6 h-6 text-red-500" strokeWidth={2.5} />
                    </div>
                    <span className="text-2xl font-bold text-red-500">{bearPower}</span>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Bear</span>
                </div>

                {/* Gauge */}
                <div className="relative w-40 h-24 flex items-end justify-center overflow-hidden">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="100%"
                                startAngle={180}
                                endAngle={0}
                                innerRadius={60}
                                outerRadius={80}
                                paddingAngle={2}
                                dataKey="value"
                                stroke="none"
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={entry.color} />
                                ))}
                            </Pie>
                        </PieChart>
                    </ResponsiveContainer>

                    {/* Needle */}
                    <div
                        className="absolute bottom-0 w-1 h-20 bg-slate-200 origin-bottom transition-all duration-1000 ease-out rounded-full"
                        style={{
                            transform: `rotate(${90 - needleAngle}deg)`,
                            bottom: '0px',
                            zIndex: 10
                        }}
                    >
                        <div className="w-3 h-3 bg-slate-100 rounded-full absolute bottom-0 -left-1 shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
                    </div>
                </div>

                {/* Bull Side */}
                <div className="flex flex-col items-center gap-1">
                    <div className="w-12 h-12 rounded-full bg-green-500/10 flex items-center justify-center border border-green-500/20">
                        <TrendingUp className="w-6 h-6 text-green-500" strokeWidth={2.5} />
                    </div>
                    <span className="text-2xl font-bold text-green-500">{bullPower}</span>
                    <span className="text-[10px] text-slate-400 uppercase tracking-wider">Bull</span>
                </div>

            </CardContent>
        </Card>
    );
};

export default MarketThermometer;
