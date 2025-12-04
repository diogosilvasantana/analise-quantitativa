'use client';

import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';

interface Props {
    children: ReactNode;
}

interface State {
    hasError: boolean;
    error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
    public state: State = {
        hasError: false,
        error: null,
    };

    public static getDerivedStateFromError(error: Error): State {
        return { hasError: true, error };
    }

    public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
        console.error('Uncaught error:', error, errorInfo);
    }

    public render() {
        if (this.state.hasError) {
            return (
                <div className="flex items-center justify-center min-h-[400px] p-6">
                    <Alert variant="destructive" className="max-w-md border-red-500/50 bg-red-950/30">
                        <AlertTriangle className="h-5 w-5" />
                        <AlertTitle>Algo deu errado!</AlertTitle>
                        <AlertDescription className="mt-2">
                            <p className="text-sm text-red-200 mb-4">
                                {this.state.error?.message || 'Ocorreu um erro inesperado no componente.'}
                            </p>
                            <Button
                                variant="outline"
                                className="w-full border-red-500/50 hover:bg-red-950/50 hover:text-red-200"
                                onClick={() => this.setState({ hasError: false, error: null })}
                            >
                                <RefreshCw className="mr-2 h-4 w-4" />
                                Tentar Novamente
                            </Button>
                        </AlertDescription>
                    </Alert>
                </div>
            );
        }

        return this.props.children;
    }
}
