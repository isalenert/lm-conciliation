/**
 * Página de Detalhes de uma Conciliação
 */

import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { getReconciliationDetails } from '../services/api';
import { ArrowLeft, CheckCircle, AlertCircle, Loader, Download } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function ReconciliationDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeTab, setActiveTab] = useState('matched');

  useEffect(() => {
    loadDetails();
  }, [id]);

  const loadDetails = async () => {
    try {
      setLoading(true);
      setError('');
      const details = await getReconciliationDetails(id);
      setData(details);
    } catch (err) {
      setError('Erro ao carregar detalhes: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
  };

  const formatValue = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    }).format(value);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <Loader className="w-8 h-8 text-blue-600 animate-spin" />
        </div>
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-6">
            <p className="text-red-700">{error || 'Conciliação não encontrada'}</p>
            <button
              onClick={() => navigate('/history')}
              className="mt-4 text-blue-600 hover:text-blue-700"
            >
              ← Voltar para histórico
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <button
          onClick={() => navigate('/history')}
          className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
          <ArrowLeft className="w-4 h-4" />
          Voltar para histórico
        </button>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Conciliação #{data.id}</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <p className="text-3xl font-bold text-green-600">{data.matched.length}</p>
              <p className="text-sm text-gray-600 mt-1">Conciliadas</p>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <p className="text-3xl font-bold text-yellow-600">{data.bank_only.length}</p>
              <p className="text-sm text-gray-600 mt-1">Pendentes (Banco)</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <p className="text-3xl font-bold text-orange-600">{data.internal_only.length}</p>
              <p className="text-sm text-gray-600 mt-1">Pendentes (Sistema)</p>
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <p className="text-3xl font-bold text-blue-600">
                {data.summary.match_rate.toFixed(1)}%
              </p>
              <p className="text-sm text-gray-600 mt-1">Taxa de Match</p>
            </div>
          </div>

          <div className="text-sm text-gray-600">
            <p><strong>Criado em:</strong> {new Date(data.created_at).toLocaleString('pt-BR')}</p>
            <p><strong>Arquivo Banco:</strong> {data.bank_file_name}</p>
            <p><strong>Arquivo Sistema:</strong> {data.internal_file_name}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-md">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('matched')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'matched'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <CheckCircle className="w-4 h-4 inline mr-2" />
                Conciliadas ({data.matched.length})
              </button>
              <button
                onClick={() => setActiveTab('bank_only')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'bank_only'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <AlertCircle className="w-4 h-4 inline mr-2" />
                Banco ({data.bank_only.length})
              </button>
              <button
                onClick={() => setActiveTab('internal_only')}
                className={`px-6 py-3 font-medium ${
                  activeTab === 'internal_only'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <AlertCircle className="w-4 h-4 inline mr-2" />
                Sistema ({data.internal_only.length})
              </button>
            </div>
          </div>

          <div className="p-6">
            {/* Tab Matched */}
            {activeTab === 'matched' && (
              <div className="space-y-4">
                {data.matched.map((match, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-green-50">
                    <div className="grid md:grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs font-semibold text-gray-500 mb-2">BANCO</p>
                        <p className="text-sm"><strong>Data:</strong> {formatDate(match.bank_transaction.Data)}</p>
                        <p className="text-sm"><strong>Valor:</strong> {formatValue(match.bank_transaction.Valor)}</p>
                        <p className="text-sm"><strong>Descrição:</strong> {match.bank_transaction.Descricao}</p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-gray-500 mb-2">SISTEMA</p>
                        <p className="text-sm"><strong>Data:</strong> {formatDate(match.internal_transaction.Data)}</p>
                        <p className="text-sm"><strong>Valor:</strong> {formatValue(match.internal_transaction.Valor)}</p>
                        <p className="text-sm"><strong>Descrição:</strong> {match.internal_transaction.Descricao}</p>
                      </div>
                    </div>
                    <div className="mt-2 text-right">
                      <span className="text-xs bg-green-200 text-green-800 px-2 py-1 rounded">
                        Confiança: {(match.confidence * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Tab Bank Only */}
            {activeTab === 'bank_only' && (
              <div className="space-y-3">
                {data.bank_only.map((transaction, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-yellow-50">
                    <p className="text-sm"><strong>Data:</strong> {formatDate(transaction.Data)}</p>
                    <p className="text-sm"><strong>Valor:</strong> {formatValue(transaction.Valor)}</p>
                    <p className="text-sm"><strong>Descrição:</strong> {transaction.Descricao}</p>
                  </div>
                ))}
              </div>
            )}

            {/* Tab Internal Only */}
            {activeTab === 'internal_only' && (
              <div className="space-y-3">
                {data.internal_only.map((transaction, index) => (
                  <div key={index} className="border rounded-lg p-4 bg-orange-50">
                    <p className="text-sm"><strong>Data:</strong> {formatDate(transaction.Data)}</p>
                    <p className="text-sm"><strong>Valor:</strong> {formatValue(transaction.Valor)}</p>
                    <p className="text-sm"><strong>Descrição:</strong> {transaction.Descricao}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
