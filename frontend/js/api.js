/**
 * SIMORGH PLATFORM - API Client
 * Communicates only through public Platform REST APIs
 */

class SimorghAPI {
  constructor(baseURL = '/api/v1', apiKey = null) {
    this.baseURL = baseURL;
    this.apiKey = apiKey || localStorage.getItem('simorgh_api_key');
  }

  setApiKey(key) {
    this.apiKey = key;
    localStorage.setItem('simorgh_api_key', key);
  }

  getApiKey() {
    return this.apiKey || localStorage.getItem('simorgh_api_key');
  }

  clearApiKey() {
    this.apiKey = null;
    localStorage.removeItem('simorgh_api_key');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add API key authentication
    if (this.apiKey) {
      headers['Authorization'] = `Bearer ${this.apiKey}`;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new APIError(error.detail || `HTTP ${response.status}`, response.status);
      }

      // Handle no content responses
      if (response.status === 204) {
        return null;
      }

      return await response.json();
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      throw new APIError('Network error or server unavailable', 0);
    }
  }

  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // Authentication
  async login(apiKey) {
    // Validate API key by making a test request
    const testKey = this.apiKey;
    this.setApiKey(apiKey);
    
    try {
      await this.get('/applications');
      return { success: true };
    } catch (error) {
      this.apiKey = testKey;
      if (testKey) {
        localStorage.setItem('simorgh_api_key', testKey);
      } else {
        localStorage.removeItem('simorgh_api_key');
      }
      throw error;
    }
  }

  logout() {
    this.clearApiKey();
  }

  // Applications
  async getApplications() {
    return this.get('/applications');
  }

  async installApplication(slug) {
    return this.post('/applications/install', { slug });
  }

  async getInstalledApplications() {
    return this.get('/applications/installed');
  }

  // Credentials (API Keys)
  async getCredentials() {
    return this.get('/credentials');
  }

  async createCredential(data) {
    return this.post('/credentials', data);
  }

  async revokeCredential(id) {
    return this.delete(`/credentials/${id}`);
  }

  // Usage
  async getUsage(filters = {}) {
    const params = new URLSearchParams();
    if (filters.workspace_id) params.append('workspace_id', filters.workspace_id);
    if (filters.application_id) params.append('application_id', filters.application_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    const queryString = params.toString();
    return this.get(`/usage${queryString ? '?' + queryString : ''}`);
  }

  // Billing
  async getCreditAccount() {
    return this.get('/billing/account');
  }

  async getTransactions() {
    return this.get('/billing/transactions');
  }

  async getSubscription() {
    return this.get('/billing/subscription');
  }

  // Knowledge Spaces
  async getKnowledgeSpaces() {
    return this.get('/knowledge/spaces');
  }

  async createKnowledgeSpace(data) {
    return this.post('/knowledge/spaces', data);
  }

  async updateKnowledgeSpace(id, data) {
    return this.put(`/knowledge/spaces/${id}`, data);
  }

  async deleteKnowledgeSpace(id) {
    return this.delete(`/knowledge/spaces/${id}`);
  }

  // Knowledge Documents
  async getDocuments(spaceId) {
    return this.get(`/knowledge/spaces/${spaceId}/documents`);
  }

  async uploadDocument(spaceId, formData) {
    return this.request(`/knowledge/spaces/${spaceId}/documents`, {
      method: 'POST',
      body: formData,
      headers: {}, // Don't set Content-Type for multipart/form-data
    });
  }

  async getDocument(documentId) {
    return this.get(`/knowledge/documents/${documentId}`);
  }

  async deleteDocument(documentId) {
    return this.delete(`/knowledge/documents/${documentId}`);
  }

  // Search
  async searchKnowledge(spaceId, query, options = {}) {
    const params = new URLSearchParams({ q: query });
    if (options.limit) params.append('limit', options.limit);
    
    return this.get(`/knowledge/spaces/${spaceId}/search?${params.toString()}`);
  }

  // Audit Events
  async getAuditEvents(filters = {}) {
    const params = new URLSearchParams();
    if (filters.event_type) params.append('event_type', filters.event_type);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    
    const queryString = params.toString();
    return this.get(`/audit/events${queryString ? '?' + queryString : ''}`);
  }
}

class APIError extends Error {
  constructor(message, status) {
    super(message);
    this.name = 'APIError';
    this.status = status;
  }
}

// Export for use in other modules
window.SimorghAPI = SimorghAPI;
window.APIError = APIError;
