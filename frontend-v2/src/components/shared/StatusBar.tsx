interface StatusBarProps {
    isConnected: boolean;
    lastUpdate: string | null;
}

export function StatusBar({ isConnected, lastUpdate }: StatusBarProps) {
    return (
        <div className="bg-slate-800/50 border-b border-slate-700 px-4 py-3">
            <div className="container mx-auto flex items-center justify-between text-sm">
                <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 animate-pulse' : 'bg-red-400'}`} />
                    <span className="text-slate-400">
                        Status: {isConnected ? <span className="text-emerald-400">✅ Conectado</span> : <span className="text-red-400">❌ Desconectado</span>}
                    </span>
                </div>
                <span className="text-slate-500">
                    Última atualização: {lastUpdate || 'N/A'}
                </span>
            </div>
        </div>
    );
}
