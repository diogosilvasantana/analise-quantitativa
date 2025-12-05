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

const MarketThermometer: React.FC<MarketThermometerProps> = ({ title, bullPower, bearPower, maxPower = 10 }) => {
    // Calculate Net Score for Needle Position
    // Range: -Max to +Max. Needle should be from 0 to 180 degrees.
    // Let's normalize:
    // Net = Bull - Bear.
    // If Bull=10, Bear=0 -> Net=10 -> Full Green (180 deg)
    // If Bull=0, Bear=10 -> Net=-10 -> Full Red (0 deg)
    // If Bull=5, Bear=5 -> Net=0 -> Middle (90 deg)

    const netScore = bullPower - bearPower;
    const totalRange = maxPower * 2; // -10 to +10 = 20 range
    const normalizedScore = Math.min(Math.max(netScore, -maxPower), maxPower); // Clamp
    const percentage = ((normalizedScore + maxPower) / totalRange) * 100;

    // Gauge Data (Background Arc)
    const data = [
        { name: 'Bearish', value: 1, color: '#ef4444' }, // Red
        { name: 'Neutral', value: 1, color: '#eab308' }, // Yellow
        { name: 'Bullish', value: 1, color: '#22c55e' }, // Green
    ];

    // Needle Rotation
    // 0% = 180deg (Left/Red) ? No, usually Gauge goes Left to Right.
    // Let's say Left is Bear (Red), Right is Bull (Green).
    // 0 deg is usually 3 o'clock in Recharts. 180 is 9 o'clock.
    // We want startAngle={180} endAngle={0}.
    // 180 deg = Left (Bear). 0 deg = Right (Bull).
    // If percentage is 0% (Full Bear), angle should be 180.
    // If percentage is 100% (Full Bull), angle should be 0.
    // Angle = 180 - (percentage/100 * 180)

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
                    <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center border border-red-500/20">
                        <TrendingDown className="w-6 h-6 text-red-500" />
                    </div>
                    <span className="text-2xl font-bold text-red-500">{bearPower}</span>
                    <span className="text-[10px] text-slate-500 uppercase">Vendedores</span>
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
                            transform: `rotate(${90 - needleAngle}deg)`, // Correct rotation: 0deg(Bull) -> 90deg(Right), 180deg(Bear) -> -90deg(Left)
                            bottom: '0px',
                            zIndex: 10
                        }}
                    >
                        <div className="w-3 h-3 bg-slate-100 rounded-full absolute bottom-0 -left-1 shadow-[0_0_10px_rgba(255,255,255,0.5)]" />
                    </div>
                </div>

                {/* Bull Side */}
                <div className="flex flex-col items-center gap-1">
                    <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center border border-green-500/20">
                        <TrendingUp className="w-6 h-6 text-green-500" />
                    </div>
                    <span className="text-2xl font-bold text-green-500">{bullPower}</span>
                    <span className="text-[10px] text-slate-500 uppercase">Compradores</span>
                </div>

            </CardContent>
        </Card>
    );
};

export default MarketThermometer;
