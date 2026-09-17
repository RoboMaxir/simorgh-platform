/**
 * SIMORGH PLATFORM - Dashboard Application Logic
 */

class DashboardApp {
  constructor() {
    this.api = new SimorghAPI();
    this.currentPage = null;
    this.init();
  }

  init() {
    // Check authentication
    if (!this.api.getApiKey() && !window.location.pathname.endsWith('login.html')) {
      window.location.href = 'login.html';
      return;
    }

    // Initialize navigation
    this.initNavigation();
    
    // Load current page
    this.loadPage();
  }

  initNavigation() {
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
      link.addEventListener('click', (e) => {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('#')) {
          navLinks.forEach(l => l.classList.remove('active'));
          link.classList.add('active');
        }
      });
    });

    // Set active link based on current page
    const path = window.location.pathname;
    navLinks.forEach(link => {
      const href = link.getAttribute('href');
      if (href && path.endsWith(href)) {
        link.classList.add('active');
      }
    });

    // Logout handler
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
      logoutBtn.addEventListener('click', () => this.handleLogout());
    }
  }

  loadPage() {
    const path = window.location.pathname;
    
    if (path.endsWith('dashboard.html') || path.endsWith('/')) {
      this.loadDashboard();
    } else if (path.endsWith('applications.html')) {
      this.loadApplications();
    } else if (path.endsWith('credentials.html')) {
      this.loadCredentials();
    } else if (path.endsWith('billing.html')) {
      this.loadBilling();
    } else if (path.endsWith('usage.html')) {
      this.loadUsage();
    } else if (path.endsWith('knowledge.html')) {
      this.loadKnowledge();
    } else if (path.endsWith('logs.html')) {
      this.loadLogs();
    }
  }

  async loadDashboard() {
    try {
      // Load credit balance
      const account = await this.api.getCreditAccount().catch(() => null);
      if (account) {
        const balanceEl = document.getElementById('credit-balance');
        if (balanceEl) {
          balanceEl.textContent = `${account.balance?.toLocaleString() || 0} ${account.currency || 'credits'}`;
        }
      }

      // Load usage summary
      const usage = await this.api.getUsage().catch(() => null);
      if (usage) {
        const requestsEl = document.getElementById('total-requests');
        const tokensEl = document.getElementById('total-tokens');
        const costEl = document.getElementById('total-cost');
        
        if (requestsEl) requestsEl.textContent = (usage.total_requests || 0).toLocaleString();
        if (tokensEl) tokensEl.textContent = ((usage.total_input_tokens || 0) + (usage.total_output_tokens || 0)).toLocaleString();
        if (costEl) costEl.textContent = (usage.total_cost || 0).toFixed(2);
      }

      // Load applications count
      const apps = await this.api.getInstalledApplications().catch(() => []);
      const appsEl = document.getElementById('total-apps');
      if (appsEl) appsEl.textContent = apps.length;

      // Load recent transactions
      const transactions = await this.api.getTransactions().catch(() => []);
      this.renderTransactionsTable(transactions.slice(0, 5));

    } catch (error) {
      console.error('Dashboard load error:', error);
      this.showError('Failed to load dashboard data');
    }
  }

  async loadApplications() {
    try {
      const container = document.getElementById('applications-list');
      if (!container) return;

      container.innerHTML = '<div class="card"><p>Loading applications...</p></div>';

      const [available, installed] = await Promise.all([
        this.api.getApplications().catch(() => []),
        this.api.getInstalledApplications().catch(() => [])
      ]);

      const installedIds = new Set(installed.map(a => a.application_id));

      if (available.length === 0) {
        container.innerHTML = '<div class="card"><p>No applications available.</p></div>';
        return;
      }

      container.innerHTML = available.map(app => {
        const isInstalled = installedIds.has(app.id);
        return `
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">${app.name}</h3>
              ${isInstalled 
                ? '<span class="badge badge-success">Installed</span>' 
                : '<button class="btn btn-primary btn-sm" onclick="app.installApplication(\'' + app.slug + '\')">Install</button>'}
            </div>
            <div class="card-body">
              <p>${app.description || 'No description available'}</p>
              <p class="mt-4"><strong>Slug:</strong> ${app.slug}</p>
              <p><strong>Status:</strong> ${app.status}</p>
            </div>
          </div>
        `;
      }).join('');

    } catch (error) {
      console.error('Applications load error:', error);
      this.showError('Failed to load applications');
    }
  }

  async installApplication(slug) {
    try {
      await this.api.installApplication(slug);
      this.showSuccess('Application installed successfully');
      setTimeout(() => this.loadApplications(), 500);
    } catch (error) {
      console.error('Install error:', error);
      this.showError('Failed to install application: ' + error.message);
    }
  }

  async loadCredentials() {
    try {
      const container = document.getElementById('credentials-list');
      if (!container) return;

      container.innerHTML = '<div class="table-container"><table class="data-table"><thead><tr><th>Name</th><th>Key Prefix</th><th>Scopes</th><th>Expires</th><th>Last Used</th><th>Status</th><th>Actions</th></tr></thead><tbody>Loading...</tbody></table></div>';

      const credentials = await this.api.getCredentials().catch(() => []);

      if (credentials.length === 0) {
        container.innerHTML = '<div class="card"><p>No API keys found. Create one to get started.</p></div>';
        return;
      }

      const tbody = credentials.map(cred => {
        const isExpired = cred.expires_at && new Date(cred.expires_at) < new Date();
        const isRevoked = cred.revoked_at !== null;
        let statusBadge = '<span class="badge badge-success">Active</span>';
        if (isRevoked) {
          statusBadge = '<span class="badge badge-danger">Revoked</span>';
        } else if (isExpired) {
          statusBadge = '<span class="badge badge-warning">Expired</span>';
        }

        return `
          <tr>
            <td>${cred.name || 'Unnamed Key'}</td>
            <td><code>${cred.key_prefix}</code></td>
            <td>${cred.scopes ? cred.scopes.map(s => `<span class="badge badge-info">${s}</span>`).join(' ') : '<span class="text-secondary">All</span>'}</td>
            <td>${cred.expires_at ? new Date(cred.expires_at).toLocaleDateString() : 'Never'}</td>
            <td>${cred.last_used_at ? new Date(cred.last_used_at).toLocaleString() : 'Never'}</td>
            <td>${statusBadge}</td>
            <td>
              ${!isRevoked ? `<button class="btn btn-danger btn-sm" onclick="app.revokeCredential('${cred.id}')">Revoke</button>` : '-'}
            </td>
          </tr>
        `;
      }).join('');

      container.innerHTML = `<div class="table-container"><table class="data-table"><thead><tr><th>Name</th><th>Key Prefix</th><th>Scopes</th><th>Expires</th><th>Last Used</th><th>Status</th><th>Actions</th></tr></thead><tbody>${tbody}</tbody></table></div>`;

    } catch (error) {
      console.error('Credentials load error:', error);
      this.showError('Failed to load credentials');
    }
  }

  async revokeCredential(id) {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await this.api.revokeCredential(id);
      this.showSuccess('API key revoked successfully');
      setTimeout(() => this.loadCredentials(), 500);
    } catch (error) {
      console.error('Revoke error:', error);
      this.showError('Failed to revoke API key: ' + error.message);
    }
  }

  async loadBilling() {
    try {
      const [account, transactions, subscription] = await Promise.all([
        this.api.getCreditAccount().catch(() => null),
        this.api.getTransactions().catch(() => []),
        this.api.getSubscription().catch(() => null)
      ]);

      // Update balance
      const balanceEl = document.getElementById('current-balance');
      if (balanceEl && account) {
        balanceEl.textContent = `${account.balance?.toLocaleString() || 0} ${account.currency || 'credits'}`;
      }

      // Update subscription info
      const planEl = document.getElementById('subscription-plan');
      if (planEl && subscription) {
        planEl.textContent = subscription.plan_name || 'No active subscription';
      }

      // Render transactions
      this.renderTransactionsTable(transactions);

    } catch (error) {
      console.error('Billing load error:', error);
      this.showError('Failed to load billing information');
    }
  }

  renderTransactionsTable(transactions) {
    const container = document.getElementById('transactions-table');
    if (!container) return;

    if (!transactions || transactions.length === 0) {
      container.innerHTML = '<p>No transactions found.</p>';
      return;
    }

    const rows = transactions.map(tx => `
      <tr>
        <td>${new Date(tx.created_at).toLocaleString()}</td>
        <td><span class="badge badge-${tx.transaction_type === 'credit' ? 'success' : 'info'}">${tx.transaction_type}</span></td>
        <td>${tx.amount > 0 ? '+' : ''}${tx.amount.toLocaleString()}</td>
        <td>${tx.reference_type || '-'}</td>
        <td><code>${tx.reference_id?.substring(0, 8)}...</code></td>
        <td>${tx.balance_after?.toLocaleString() || '-'}</td>
      </tr>
    `).join('');

    container.innerHTML = `
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Type</th>
              <th>Amount</th>
              <th>Reference Type</th>
              <th>Reference ID</th>
              <th>Balance After</th>
            </tr>
          </thead>
          <tbody>${rows}</tbody>
        </table>
      </div>
    `;
  }

  async loadUsage() {
    try {
      const container = document.getElementById('usage-data');
      if (!container) return;

      // Get date filters
      const startDate = document.getElementById('start-date')?.value;
      const endDate = document.getElementById('end-date')?.value;

      const filters = {};
      if (startDate) filters.start_date = startDate;
      if (endDate) filters.end_date = endDate;

      const usage = await this.api.getUsage(filters);

      container.innerHTML = `
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-label">Total Requests</div>
            <div class="stat-value">${(usage.total_requests || 0).toLocaleString()}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Input Tokens</div>
            <div class="stat-value">${(usage.total_input_tokens || 0).toLocaleString()}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Output Tokens</div>
            <div class="stat-value">${(usage.total_output_tokens || 0).toLocaleString()}</div>
          </div>
          <div class="stat-card">
            <div class="stat-label">Total Cost</div>
            <div class="stat-value">${(usage.total_cost || 0).toFixed(2)}</div>
          </div>
        </div>
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Usage Details</h3>
          </div>
          <div class="card-body">
            <p>Filter by date range to see specific usage data.</p>
          </div>
        </div>
      `;

    } catch (error) {
      console.error('Usage load error:', error);
      this.showError('Failed to load usage data');
    }
  }

  async loadKnowledge() {
    try {
      const container = document.getElementById('knowledge-spaces');
      if (!container) return;

      const spaces = await this.api.getKnowledgeSpaces().catch(() => []);

      if (spaces.length === 0) {
        container.innerHTML = `
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">Knowledge Spaces</h3>
              <button class="btn btn-primary" onclick="app.showCreateSpaceModal()">Create Space</button>
            </div>
            <div class="card-body">
              <p>No knowledge spaces yet. Create your first space to start organizing documents.</p>
            </div>
          </div>
        `;
        return;
      }

      container.innerHTML = `
        <div class="card">
          <div class="card-header">
            <h3 class="card-title">Knowledge Spaces</h3>
            <button class="btn btn-primary" onclick="app.showCreateSpaceModal()">Create Space</button>
          </div>
        </div>
        ${spaces.map(space => `
          <div class="card">
            <div class="card-header">
              <h3 class="card-title">${space.name}</h3>
              <div class="flex gap-2">
                <button class="btn btn-secondary btn-sm" onclick="app.viewDocuments('${space.id}')">View Documents</button>
                <button class="btn btn-danger btn-sm" onclick="app.deleteSpace('${space.id}')">Delete</button>
              </div>
            </div>
            <div class="card-body">
              <p>${space.description || 'No description'}</p>
              <p class="mt-4"><strong>Documents:</strong> ${space.document_count || 0}</p>
            </div>
          </div>
        `).join('')}
      `;

    } catch (error) {
      console.error('Knowledge load error:', error);
      this.showError('Failed to load knowledge spaces');
    }
  }

  showCreateSpaceModal() {
    const modal = document.getElementById('create-space-modal');
    if (modal) {
      modal.classList.add('active');
    }
  }

  closeCreateSpaceModal() {
    const modal = document.getElementById('create-space-modal');
    if (modal) {
      modal.classList.remove('active');
    }
  }

  async handleCreateSpace(event) {
    event.preventDefault();
    const form = event.target;
    const name = form.querySelector('[name="space-name"]').value;
    const description = form.querySelector('[name="space-description"]')?.value || '';

    try {
      await this.api.createKnowledgeSpace({ name, description });
      this.showSuccess('Knowledge space created successfully');
      this.closeCreateSpaceModal();
      form.reset();
      setTimeout(() => this.loadKnowledge(), 500);
    } catch (error) {
      console.error('Create space error:', error);
      this.showError('Failed to create space: ' + error.message);
    }
  }

  async viewDocuments(spaceId) {
    // Navigate to documents view or show modal
    alert(`Viewing documents for space: ${spaceId}\n(This would navigate to a documents list page)`);
  }

  async deleteSpace(spaceId) {
    if (!confirm('Are you sure you want to delete this knowledge space? All documents will be deleted.')) {
      return;
    }

    try {
      await this.api.deleteKnowledgeSpace(spaceId);
      this.showSuccess('Knowledge space deleted successfully');
      setTimeout(() => this.loadKnowledge(), 500);
    } catch (error) {
      console.error('Delete space error:', error);
      this.showError('Failed to delete space: ' + error.message);
    }
  }

  async loadLogs() {
    try {
      const container = document.getElementById('audit-logs');
      if (!container) return;

      const events = await this.api.getAuditEvents().catch(() => []);

      if (events.length === 0) {
        container.innerHTML = '<div class="card"><p>No audit events found.</p></div>';
        return;
      }

      const rows = events.map(event => `
        <tr>
          <td>${new Date(event.created_at).toLocaleString()}</td>
          <td><span class="badge badge-info">${event.event_type}</span></td>
          <td>${event.application_id || '-'}</td>
          <td><code>${event.payload ? JSON.stringify(event.payload).substring(0, 50) + '...' : '-'}</code></td>
        </tr>
      `).join('');

      container.innerHTML = `
        <div class="table-container">
          <table class="data-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Event Type</th>
                <th>Application</th>
                <th>Payload</th>
              </tr>
            </thead>
            <tbody>${rows}</tbody>
          </table>
        </div>
      `;

    } catch (error) {
      console.error('Logs load error:', error);
      this.showError('Failed to load audit logs');
    }
  }

  async handleLogout() {
    this.api.logout();
    window.location.href = 'login.html';
  }

  showError(message) {
    this.showNotification(message, 'error');
  }

  showSuccess(message) {
    this.showNotification(message, 'success');
  }

  showNotification(message, type = 'info') {
    // Simple notification - could be enhanced with a proper toast system
    const colors = {
      error: '#ef4444',
      success: '#10b981',
      info: '#2563eb'
    };

    const notification = document.createElement('div');
    notification.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 1rem 1.5rem;
      background: ${colors[type] || colors.info};
      color: white;
      border-radius: 8px;
      box-shadow: 0 4px 6px rgba(0,0,0,0.1);
      z-index: 9999;
      animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    document.body.appendChild(notification);

    setTimeout(() => {
      notification.style.opacity = '0';
      setTimeout(() => notification.remove(), 300);
    }, 3000);
  }
}

// Initialize app when DOM is ready
let app;
document.addEventListener('DOMContentLoaded', () => {
  app = new DashboardApp();
});
