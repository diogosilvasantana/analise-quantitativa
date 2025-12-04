export function Header() {
    return (
        <header className="bg-slate-900/80 backdrop-blur border-b border-slate-800">
            <div className="container mx-auto px-4 py-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold bg-gradient-to-r from-emerald-400 to-cyan-400 bg-clip-text text-transparent">
                            AI-TRADER-PRO
                        </h1>
                        <p className="text-slate-400 text-sm mt-1">Dashboard de Análise em Tempo Real</p>
                    </div>
                    <div className="text-right">
                        <p className="text-sm text-slate-400">Versão 2.0</p>
                    </div>
                </div>
            </div>
        </header>
    );
}
