/**
 * Página de Configurações
 */

import { useState, useEffect } from 'react';
import { getSettings, updateSettings } from '../services/api';
import { Save, AlertCircle, CheckCircle } from 'lucide-react';
import Navbar from '../components/Navbar';

export default function Settings() {
  const [settings, setSettings] = useState({
    date_tolerance_days: 1,
    value_tolerance: 0.02,
    similarity_threshold: 0.7,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  useEffect(() => {
    loadSettings();
  }, []);

  const loadSettings = async () => {
    try {
      setLoading(true);
      const data = await getSettings();
      setSettings(data);
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao carregar configurações' });
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage({ type: '', text: '' });
      
      await updateSettings(settings);
      
      setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' });
      
      // Limpar mensagem após 3 segundos
      setTimeout(() => {
        setMessage({ type: '', text: '' });
      }, 3000);
    } catch (err) {
      setMessage({ type: 'error', text: 'Erro ao salvar configurações' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="flex items-center justify-center h-96">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">Configurações</h2>
          <p className="text-gray-600 mt-2">
            Configure as tolerâncias padrão para suas conciliações
          </p>
        </div>

        {message.text && (
          <div
            className={`mb-6 p-4 rounded-lg flex items-start ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200'
                : 'bg-red-50 border border-red-200'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 text-green-500 mt-0.5 mr-3" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
            )}
            <p
              className={
                message.type === 'success' ? 'text-green-700' : 'text-red-700'
              }
            >
              {message.text}
            </p>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-md p-8">
          <div className="space-y-8">
            {/* Tolerância de Data */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tolerância de Data (dias): {settings.date_tolerance_days}
              </label>
              <input
                type="range"
                min="0"
                max="7"
                value={settings.date_tolerance_days}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    date_tolerance_days: parseInt(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-sm text-gray-500 mt-2">
                Permite que transações com datas próximas sejam conciliadas.
                Exemplo: com tolerância de 1 dia, uma transação de 10/11 pode
                ser conciliada com 11/11.
              </p>
            </div>

            {/* Tolerância de Valor */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tolerância de Valor: R$ {settings.value_tolerance.toFixed(2)}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={settings.value_tolerance}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    value_tolerance: parseFloat(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-sm text-gray-500 mt-2">
                Diferença máxima permitida entre valores. Útil para ajustes de
                IOF, taxas, etc. Exemplo: R$ 100,00 pode conciliar com R$
                100,02.
              </p>
            </div>

            {/* Similaridade Mínima */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Similaridade Mínima:{' '}
                {(settings.similarity_threshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.5"
                max="1"
                step="0.05"
                value={settings.similarity_threshold}
                onChange={(e) =>
                  setSettings({
                    ...settings,
                    similarity_threshold: parseFloat(e.target.value),
                  })
                }
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-sm text-gray-500 mt-2">
                Percentual mínimo de similaridade entre descrições. Quanto
                maior, mais restritivo. Exemplo: 70% permite variações como
                "PIX João Silva" e "Pix Joao Silva".
              </p>
            </div>
          </div>

          {/* Preview das Configurações */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-900 mb-2">
              📋 Resumo das Configurações:
            </h3>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>
                • Datas podem diferir em até{' '}
                <strong>{settings.date_tolerance_days} dia(s)</strong>
              </li>
              <li>
                • Valores podem diferir em até{' '}
                <strong>R$ {settings.value_tolerance.toFixed(2)}</strong>
              </li>
              <li>
                • Descrições devem ter pelo menos{' '}
                <strong>
                  {(settings.similarity_threshold * 100).toFixed(0)}% de
                  similaridade
                </strong>
              </li>
            </ul>
          </div>

          <button
            onClick={handleSave}
            disabled={saving}
            className="w-full mt-8 py-3 px-6 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold rounded-lg flex items-center justify-center transition-colors"
          >
            <Save className="w-5 h-5 mr-2" />
            {saving ? 'Salvando...' : 'Salvar Configurações'}
          </button>
        </div>

        {/* Informações Adicionais */}
        <div className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <h3 className="font-semibold text-yellow-900 mb-2">
            💡 Dica:
          </h3>
          <p className="text-sm text-yellow-800">
            Essas configurações serão usadas como padrão em todas as suas
            próximas conciliações. Você ainda pode ajustá-las individualmente
            na página de mapeamento antes de executar cada conciliação.
          </p>
        </div>
      </main>
    </div>
  );
}
