/**
 * Página de Upload de Arquivos
 */

import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, FileText, AlertCircle } from 'lucide-react';

function UploadPage() {
  const navigate = useNavigate();
  const [files, setFiles] = useState({
    bank: null,
    internal: null,
  });
  const [dragActive, setDragActive] = useState({
    bank: false,
    internal: false,
  });
  const [error, setError] = useState('');

  // Handler de drag and drop
  const handleDrag = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive({ ...dragActive, [fileType]: true });
    } else if (e.type === 'dragleave') {
      setDragActive({ ...dragActive, [fileType]: false });
    }
  };

  const handleDrop = (e, fileType) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive({ ...dragActive, [fileType]: false });

    const file = e.dataTransfer.files[0];
    handleFileSelect(file, fileType);
  };

  const handleFileSelect = (file, fileType) => {
    setError('');

    // Validar arquivo
    if (!file) return;

    const validExtensions = ['.csv', '.pdf'];
    const fileExtension = file.name.substring(file.name.lastIndexOf('.')).toLowerCase();

    if (!validExtensions.includes(fileExtension)) {
      setError('Formato inválido. Use CSV ou PDF.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      setError('Arquivo muito grande. Máximo: 5MB');
      return;
    }

    setFiles({ ...files, [fileType]: file });
  };

  const handleContinue = () => {
    if (files.bank && files.internal) {
      // Navegar para página de mapeamento
      navigate('/mapping', { state: { files } });
    } else {
      setError('Selecione os dois arquivos para continuar');
    }
  };

  const FileUploadZone = ({ fileType, title, description }) => (
    <div
      className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
        dragActive[fileType]
          ? 'border-blue-500 bg-blue-50'
          : files[fileType]
          ? 'border-green-500 bg-green-50'
          : 'border-gray-300 hover:border-gray-400'
      }`}
      onDragEnter={(e) => handleDrag(e, fileType)}
      onDragLeave={(e) => handleDrag(e, fileType)}
      onDragOver={(e) => handleDrag(e, fileType)}
      onDrop={(e) => handleDrop(e, fileType)}
    >
      <input
        type="file"
        accept=".csv,.pdf"
        onChange={(e) => handleFileSelect(e.target.files[0], fileType)}
        className="hidden"
        id={`file-${fileType}`}
      />
      
      <label htmlFor={`file-${fileType}`} className="cursor-pointer">
        <div className="flex flex-col items-center">
          {files[fileType] ? (
            <>
              <FileText className="w-12 h-12 text-green-500 mb-2" />
              <p className="font-semibold text-green-700">{files[fileType].name}</p>
              <p className="text-sm text-gray-500 mt-1">
                {(files[fileType].size / 1024).toFixed(2)} KB
              </p>
            </>
          ) : (
            <>
              <Upload className="w-12 h-12 text-gray-400 mb-2" />
              <p className="font-semibold text-gray-700">{title}</p>
              <p className="text-sm text-gray-500 mt-1">{description}</p>
              <p className="text-xs text-gray-400 mt-2">CSV ou PDF • Máx. 5MB</p>
            </>
          )}
        </div>
      </label>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold text-gray-900">
            LM Conciliation
          </h1>
          <p className="text-gray-600 mt-1">
            Sistema de Conciliação Bancária Automatizado
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-semibold mb-2">Upload de Arquivos</h2>
          <p className="text-gray-600 mb-6">
            Faça upload dos dois arquivos que deseja conciliar
          </p>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 mr-3" />
              <p className="text-red-700">{error}</p>
            </div>
          )}

          {/* Upload Zones */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <FileUploadZone
              fileType="bank"
              title="Extrato Bancário"
              description="Arquivo do banco (CSV ou PDF)"
            />
            <FileUploadZone
              fileType="internal"
              title="Sistema Interno"
              description="Arquivo do seu sistema (CSV)"
            />
          </div>

          {/* Continue Button */}
          <button
            onClick={handleContinue}
            disabled={!files.bank || !files.internal}
            className={`w-full py-3 px-6 rounded-lg font-semibold transition-colors ${
              files.bank && files.internal
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }`}
          >
            Continuar para Mapeamento
          </button>

          {/* Instructions */}
          <div className="mt-8 p-4 bg-blue-50 rounded-lg">
            <h3 className="font-semibold text-blue-900 mb-2">📋 Instruções:</h3>
            <ol className="list-decimal list-inside text-sm text-blue-800 space-y-1">
              <li>Faça upload do extrato bancário (CSV ou PDF)</li>
              <li>Faça upload do arquivo do sistema interno (CSV)</li>
              <li>Na próxima etapa, você mapeará as colunas</li>
              <li>O sistema realizará a conciliação automática</li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  );
}

export default UploadPage;
