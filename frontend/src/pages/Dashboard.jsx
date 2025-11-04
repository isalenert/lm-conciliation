/**
 * Dashboard - Página principal após login
 */

import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getStatistics } from '../services/api';
import { LogOut, Upload, History, Settings, BarChart3, Loader } from 'lucide-react';

export default function Dashboard() {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStatistics();
  }, []);

  const loadStatistics = async () => {
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err) {
      console.error('Erro ao carregar estatísticas:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navbar */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold text-blue-600">LM Conciliation</h1>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
            >
              <LogOut className="w-4 h-4" />
              Sair
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Welcome */}
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            Bem-vindo, {user?.name?.split(' ')[0]}! 👋
          </h2>
          <p className="text-gray-600 mt-2">
            O que você gostaria de fazer hoje?
          </p>
        </div>

        {/* Action Cards */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <button
            onClick={() => navigate('/upload')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left"
          >
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Upload className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Nova Conciliação
            </h3>
            <p className="text-sm text-gray-600">
              Faça upload de arquivos e inicie uma nova conciliação
            </p>
          </button>

          <button
            onClick={() => navigate('/history')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left"
          >
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <History className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Histórico
            </h3>
            <p className="text-sm text-gray-600">
              Veja suas conciliações anteriores
            </p>
          </button>

          <button
            onClick={() => navigate('/settings')}
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left opacity-75 cursor-not-allowed"
            disabled
          >
            <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
              <Settings className="w-6 h-6 text-purple-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Configurações
            </h3>
            <p className="text-sm text-gray-600">
              Em breve: Configure tolerâncias
            </p>
          </button>

          <button
            className="bg-white p-6 rounded-lg shadow-md hover:shadow-lg transition-shadow text-left opacity-75 cursor-not-allowed"
            disabled
          >
            <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center mb-4">
              <BarChart3 className="w-6 h-6 text-orange-600" />
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              Relatórios
            </h3>
            <p className="text-sm text-gray-600">
              Em breve: Análises e insights
            </p>
          </button>
        </div>

        {/* Quick Stats */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            Estatísticas Rápidas
          </h3>
          {loading ? (
            <div className="flex justify-center py-8">
              <Loader className="w-8 h-8 text-blue-600 animate-spin" />
            </div>
          ) : stats && stats.total_reconciliations > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <p className="text-3xl font-bold text-blue-600">{stats.total_reconciliations}</p>
                <p className="text-sm text-gray-600 mt-1">Conciliações Realizadas</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-green-600">{stats.average_match_rate.toFixed(1)}%</p>
                <p className="text-sm text-gray-600 mt-1">Taxa Média de Match</p>
              </div>
              <div className="text-center">
                <p className="text-3xl font-bold text-purple-600">{stats.total_transactions}</p>
                <p className="text-sm text-gray-600 mt-1">Transações Processadas</p>
              </div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center">
                  <p className="text-3xl font-bold text-blue-600">0</p>
                  <p className="text-sm text-gray-600 mt-1">Conciliações Realizadas</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-green-600">0%</p>
                  <p className="text-sm text-gray-600 mt-1">Taxa Média de Match</p>
                </div>
                <div className="text-center">
                  <p className="text-3xl font-bold text-purple-600">0</p>
                  <p className="text-sm text-gray-600 mt-1">Transações Processadas</p>
                </div>
              </div>
              <p className="text-center text-gray-500 text-sm mt-6">
                Faça sua primeira conciliação para ver suas estatísticas!
              </p>
            </>
          )}
        </div>

        {/* Quick Start Guide */}
        <div className="mt-8 bg-blue-50 rounded-lg p-6 border border-blue-200">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            🚀 Guia Rápido
          </h3>
          <ol className="space-y-2 text-blue-800">
            <li className="flex items-start">
              <span className="font-semibold mr-2">1.</span>
              <span>Clique em "Nova Conciliação" e faça upload dos seus arquivos (CSV ou PDF)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">2.</span>
              <span>Mapeie as colunas dos seus arquivos</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">3.</span>
              <span>Ajuste as configurações de tolerância (opcional)</span>
            </li>
            <li className="flex items-start">
              <span className="font-semibold mr-2">4.</span>
              <span>Execute a conciliação e veja os resultados!</span>
            </li>
          </ol>
        </div>
      </main>
    </div>
  );
}
