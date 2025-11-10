/**
 * Página de Mapeamento de Colunas - MELHORADA
 */

import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { processCSVLocal, uploadFiles, reconcileTransactions, getSettings } from '../services/api';
import { ArrowRight, Settings, Loader, Table } from 'lucide-react';
import Navbar from '../components/Navbar';

function MappingPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const { files } = location.state || {};

  const [bankData, setBankData] = useState(null);
  const [internalData, setInternalData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState('');

  const [mapping, setMapping] = useState({
    date_col: '',
    value_col: '',
    desc_col: '',
    id_col: '',
  });

  const [config, setConfig] = useState({
    date_tolerance: 1,
    value_tolerance: 0.02,
    similarity_threshold: 0.7,
  });

  useEffect(() => {
    if (!files || !files.bank || !files.internal) {
      navigate('/upload');
      return;
    }
    loadFiles();
    loadUserSettings();
  }, [files, navigate]);

  const loadUserSettings = async () => {
    try {
      const settings = await getSettings();
      setConfig({
        date_tolerance: settings.date_tolerance_days,
        value_tolerance: settings.value_tolerance,
        similarity_threshold: settings.similarity_threshold,
      });
    } catch (err) {
      console.log('Usando configurações padrão');
    }
  };

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError('');

       const [bankResponse, internalResponse] = await Promise.all([
       processCSVLocal(files.bank),
       processCSVLocal(files.internal),
      ]);

      setBankData(bankResponse);
      setInternalData(internalResponse);

      // Auto-detectar colunas
      const bankCols = bankResponse.columns;
      const internalCols = internalResponse.columns;

      const detectColumn = (keywords) => {
        const allCols = [...bankCols, ...internalCols];
        return allCols.find((col) =>
          keywords.some((keyword) => col.toLowerCase().includes(keyword))
        ) || '';
      };

      setMapping({
        date_col: detectColumn(['data', 'date']),
        value_col: detectColumn(['valor', 'value', 'amount']),
        desc_col: detectColumn(['descri', 'desc', 'historic']),
        id_col: detectColumn(['id', 'codigo', 'code']),
      });
    } catch (err) {
      setError('Erro ao processar arquivos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReconcile = async () => {
    try {
      setProcessing(true);
      setError('');

      // PASSO 1: Fazer upload dos arquivos primeiro
      const uploadResponse = await uploadFiles(files.bank, files.internal);
      
      if (!uploadResponse || !uploadResponse.bank_file || !uploadResponse.internal_file) {
        throw new Error('Erro no upload dos arquivos');
      }

      // PASSO 2: Enviar para conciliação com os nomes dos arquivos
      const reconcileData = {
        bank_file: uploadResponse.bank_file,
        internal_file: uploadResponse.internal_file,
        bank_mapping: {
          date_col: mapping.date_col,
          value_col: mapping.value_col,
          desc_col: mapping.desc_col,
        },
        internal_mapping: {
          date_col: mapping.date_col,
          value_col: mapping.value_col,
          desc_col: mapping.desc_col,
        },
        date_tolerance: config.date_tolerance,
        value_tolerance: config.value_tolerance,
        similarity_threshold: config.similarity_threshold,
      };

      const result = await reconcileTransactions(reconcileData);

      navigate('/results', { state: { results: result } });
    } catch (err) {
      setError('Erro na conciliação: ' + err.message);
      console.error('Erro completo:', err);
    } finally {
      setProcessing(false);
    }
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

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <main className="max-w-7xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* PREVIEW DOS ARQUIVOS */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
            <Table className="w-6 h-6 mr-2" />
            Preview dos Arquivos
          </h2>
          
          <div className="grid md:grid-cols-2 gap-6">
            {/* Preview Banco */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                📊 {files.bank.name}
              </h3>
              <div className="text-sm text-gray-600 mb-3">
                {bankData.rows} linhas • {bankData.columns.length} colunas
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {bankData.columns.map((col) => (
                        <th
                          key={col}
                          className="px-3 py-2 text-left font-semibold text-gray-700 border-b"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {bankData.preview.slice(0, 3).map((row, idx) => (
                      <tr key={idx} className="border-b">
                        {bankData.columns.map((col) => (
                          <td key={col} className="px-3 py-2 text-gray-600">
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Preview Sistema */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="font-semibold text-gray-900 mb-3">
                💻 {files.internal.name}
              </h3>
              <div className="text-sm text-gray-600 mb-3">
                {internalData.rows} linhas • {internalData.columns.length} colunas
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      {internalData.columns.map((col) => (
                        <th
                          key={col}
                          className="px-3 py-2 text-left font-semibold text-gray-700 border-b"
                        >
                          {col}
                        </th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {internalData.preview.slice(0, 3).map((row, idx) => (
                      <tr key={idx} className="border-b">
                        {internalData.columns.map((col) => (
                          <td key={col} className="px-3 py-2 text-gray-600">
                            {row[col]}
                          </td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        {/* MAPEAMENTO DE COLUNAS */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Mapeamento - Arquivo do Banco
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Data *
                </label>
                <select
                  value={mapping.date_col}
                  onChange={(e) => setMapping({ ...mapping, date_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {bankData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Valor *
                </label>
                <select
                  value={mapping.value_col}
                  onChange={(e) => setMapping({ ...mapping, value_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {bankData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Descrição *
                </label>
                <select
                  value={mapping.desc_col}
                  onChange={(e) => setMapping({ ...mapping, desc_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {bankData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-semibold mb-4 flex items-center">
              <Settings className="w-5 h-5 mr-2" />
              Mapeamento - Arquivo do Sistema
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Data *
                </label>
                <select
                  value={mapping.date_col}
                  onChange={(e) => setMapping({ ...mapping, date_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {internalData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Valor *
                </label>
                <select
                  value={mapping.value_col}
                  onChange={(e) => setMapping({ ...mapping, value_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {internalData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Coluna de Descrição *
                </label>
                <select
                  value={mapping.desc_col}
                  onChange={(e) => setMapping({ ...mapping, desc_col: e.target.value })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Selecione...</option>
                  {internalData?.columns.map((col) => (
                    <option key={col} value={col}>{col}</option>
                  ))}
                </select>
              </div>
            </div>
          </div>
        </div>

        {/* CONFIGURAÇÕES AVANÇADAS */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">
            Configurações Avançadas
          </h2>

          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tolerância de Data (dias): {config.date_tolerance}
              </label>
              <input
                type="range"
                min="0"
                max="7"
                value={config.date_tolerance}
                onChange={(e) => setConfig({ ...config, date_tolerance: parseInt(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Tolerância de Valor: R$ {config.value_tolerance.toFixed(2)}
              </label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.01"
                value={config.value_tolerance}
                onChange={(e) => setConfig({ ...config, value_tolerance: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Similaridade Mínima: {(config.similarity_threshold * 100).toFixed(0)}%
              </label>
              <input
                type="range"
                min="0.5"
                max="1"
                step="0.05"
                value={config.similarity_threshold}
                onChange={(e) => setConfig({ ...config, similarity_threshold: parseFloat(e.target.value) })}
                className="w-full"
              />
            </div>
          </div>
        </div>

        <button
          onClick={handleReconcile}
          disabled={processing || !mapping.date_col || !mapping.value_col || !mapping.desc_col}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 text-white font-semibold py-3 px-6 rounded-lg flex items-center justify-center transition-colors"
        >
          {processing ? (
            <>
              <Loader className="w-5 h-5 mr-2 animate-spin" />
              Processando...
            </>
          ) : (
            <>
              Executar Conciliação
              <ArrowRight className="w-5 h-5 ml-2" />
            </>
          )}
        </button>
      </main>
    </div>
  );
}

export default MappingPage;
