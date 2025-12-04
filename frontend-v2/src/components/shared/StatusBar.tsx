import { Wifi, WifiOff, Clock, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface StatusBarProps {
    isConnected: boolean;
    lastUpdate: string | null;
    onReconnect?: () => void;
}

export function StatusBar({ isConnected, lastUpdate, onReconnect }: StatusBarProps) {
    return (
        <div className="bg-slate-800/50 border-b border-slate-700 px-4 py-3">
            <div className="container mx-auto flex items-center justify-between text-sm">
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                        {isConnected ? (
                            <Wifi className="w-4 h-4 text-emerald-400 animate-pulse" />
                        ) : (
                            <WifiOff className="w-4 h-4 text-red-400" />
                        )}
                        <span className="text-slate-400">
                            Status: {isConnected ? <span className="text-emerald-400">Conectado</span> : <span className="text-red-400">Desconectado</span>}
                        </span>
                    </div>

                    {!isConnected && onReconnect && (
                        <Button
                            variant="outline"
                            size="sm"
                            className="h-6 text-xs border-slate-600 hover:bg-slate-700 text-slate-300"
                            onClick={onReconnect}
                        >
                            <RefreshCw className="w-3 h-3 mr-1" />
                            Reconectar
                        </Button>
                    )}
                </div>

                <div className="flex items-center gap-2 text-slate-500">
                    <Clock className="w-4 h-4" />
                    <span>
                        Última atualização: {lastUpdate || 'N/A'}
                    </span>
                </div>
            </div>
        </div>
    );
}
