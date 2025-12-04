import React from 'react';
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { LayoutDashboard, Settings, Activity, BarChart3, Globe, Zap } from "lucide-react";

interface DashboardLayoutProps {
    children: React.ReactNode;
    isConnected: boolean;
    lastUpdate: string | null;
}

export function DashboardLayout({ children, isConnected, lastUpdate }: DashboardLayoutProps) {
    return (
        <div className="flex min-h-screen bg-background text-foreground font-sans">
            {/* Sidebar */}
            <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col">
                <div className="p-6">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-primary to-blue-500 bg-clip-text text-transparent">
                        AI TRADER PRO
                    </h1>
                    <p className="text-xs text-muted-foreground mt-1">Institutional Analytics</p>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    <Button variant="secondary" className="w-full justify-start gap-2">
                        <LayoutDashboard size={18} />
                        Dashboard
                    </Button>
                    <Button variant="ghost" className="w-full justify-start gap-2">
                        <Activity size={18} />
                        Market Breadth
                    </Button>
                    <Button variant="ghost" className="w-full justify-start gap-2">
                        <Globe size={18} />
                        Global Indices
                    </Button>
                    <Button variant="ghost" className="w-full justify-start gap-2">
                        <BarChart3 size={18} />
                        Commodities
                    </Button>
                    <Button variant="ghost" className="w-full justify-start gap-2">
                        <Zap size={18} />
                        Rates & FX
                    </Button>
                </nav>

                <div className="p-4 border-t border-border">
                    <Button variant="ghost" className="w-full justify-start gap-2 text-muted-foreground">
                        <Settings size={18} />
                        Settings
                    </Button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 flex flex-col">
                {/* Header */}
                <header className="h-16 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between px-6 sticky top-0 z-50">
                    <div className="flex items-center gap-4">
                        <span className="text-sm font-medium text-muted-foreground">Market Status:</span>
                        <Badge variant={isConnected ? "default" : "destructive"} className={isConnected ? "bg-green-500/10 text-green-500 hover:bg-green-500/20" : ""}>
                            {isConnected ? "CONNECTED" : "DISCONNECTED"}
                        </Badge>
                    </div>

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                        <span>Last Update: <span className="text-foreground font-mono">{lastUpdate || "Waiting..."}</span></span>
                    </div>
                </header>

                {/* Dashboard Content */}
                <div className="flex-1 p-6 overflow-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
