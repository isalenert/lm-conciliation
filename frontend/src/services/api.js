/**
 * Serviço de comunicação com API
 */

import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Criar instância do axios
const api = axios.create({
  baseURL: API_URL,
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ========== UPLOAD ==========
export const uploadCSV = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// ========== CONCILIAÇÃO ==========
export const reconcileFiles = async (bankFile, internalFile, config) => {
  const formData = new FormData();
  formData.append('bank_file', bankFile);
  formData.append('internal_file', internalFile);
  formData.append('date_col', config.date_col);
  formData.append('value_col', config.value_col);
  formData.append('desc_col', config.desc_col);
  formData.append('id_col', config.id_col || '');
  formData.append('date_tolerance', config.date_tolerance);
  formData.append('value_tolerance', config.value_tolerance);
  formData.append('similarity_threshold', config.similarity_threshold);

  const response = await api.post('/api/reconcile', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// ========== HISTÓRICO ==========
export const getHistory = async () => {
  const response = await api.get('/api/history');
  return response.data;
};

export const getReconciliationDetails = async (id) => {
  const response = await api.get(`/api/history/${id}`);
  return response.data;
};

export const getStatistics = async () => {
  const response = await api.get('/api/statistics');
  return response.data;
};

export default api;
