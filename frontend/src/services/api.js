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

// ========== UPLOAD DE ARQUIVOS ==========
export const uploadFiles = async (bankFile, internalFile) => {
  const formData = new FormData();
  formData.append('bank_file', bankFile);
  formData.append('internal_file', internalFile);

  const response = await api.post('/api/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

// Processar CSV localmente para preview
export const processCSVLocal = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const text = e.target.result;
      const lines = text.split('\n').filter(line => line.trim());
      
      if (lines.length === 0) {
        reject(new Error('Arquivo vazio'));
        return;
      }
      
      // Parse CSV
      const headers = lines[0].split(',').map(h => h.trim());
      const rows = lines.slice(1).map(line => {
        const values = line.split(',');
        const row = {};
        headers.forEach((header, i) => {
          row[header] = values[i]?.trim() || '';
        });
        return row;
      });
      
      resolve({
        columns: headers,
        rows: rows.length,
        preview: rows.slice(0, 5)
      });
    };
    
    reader.onerror = () => reject(new Error('Erro ao ler arquivo'));
    reader.readAsText(file);
  });
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

// Reconciliar usando nomes de arquivos já enviados
export const reconcileTransactions = async (data) => {
  const response = await api.post('/api/reconcile', data, {
    headers: {
      'Content-Type': 'application/json',
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

// ========== CONFIGURAÇÕES ==========
export const getSettings = async () => {
  const response = await api.get('/api/settings');
  return response.data;
};

export const updateSettings = async (settings) => {
  const response = await api.put('/api/settings', settings);
  return response.data;
};

// ========== CONCILIAÇÃO MANUAL ==========
export const getPendingTransactions = async (reconciliationId) => {
  const response = await api.get(`/api/reconciliation/${reconciliationId}/pending`);
  return response.data;
};

export const createManualMatch = async (matchData) => {
  const response = await api.post('/api/manual-match', matchData);
  return response.data;
};

// ========== RECUPERAÇÃO DE SENHA ==========
export const requestPasswordReset = async (email) => {
  const response = await api.post('/api/auth/forgot-password', { email });
  return response.data;
};

export const resetPassword = async (token, newPassword) => {
  const response = await api.post('/api/auth/reset-password', {
    token,
    new_password: newPassword,
  });
  return response.data;
};

export default api;
