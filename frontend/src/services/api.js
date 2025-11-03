/**
 * Serviço de comunicação com a API
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ========== UPLOAD ==========

/**
 * Upload de arquivo CSV
 */
export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload/csv', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Upload de arquivo PDF
 */
export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// ========== CONCILIAÇÃO ==========

/**
 * Executar conciliação entre dois arquivos
 */
export const reconcileFiles = async (bankFile, internalFile, config) => {
  const formData = new FormData();
  formData.append('bank_file', bankFile);
  formData.append('internal_file', internalFile);
  
  // Adicionar configurações
  formData.append('date_col', config.date_col || 'Data');
  formData.append('value_col', config.value_col || 'Valor');
  formData.append('desc_col', config.desc_col || 'Descricao');
  if (config.id_col) formData.append('id_col', config.id_col);
  formData.append('date_tolerance', config.date_tolerance || 1);
  formData.append('value_tolerance', config.value_tolerance || 0.02);
  formData.append('similarity_threshold', config.similarity_threshold || 0.7);

  const response = await api.post('/api/reconcile', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// ========== HEALTH CHECK ==========

/**
 * Verificar status da API
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
