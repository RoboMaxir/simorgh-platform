# SIMORGH Platform Frontend

SaaS Dashboard for SIMORGH Platform - A shared infrastructure layer for AI services, Knowledge services, and Shora AI Council.

## Architecture

This frontend is a **static HTML/CSS/JavaScript** application that communicates with the Platform backend through REST APIs only.

### Key Principles

- **No business logic**: Pure platform infrastructure management
- **API-first**: All data fetched through `/api/v1/*` endpoints
- **No OrgOS features**: No ERP, manufacturing, HR, or organizational concepts
- **No Shora logic**: No council, voting, or decision-making UI

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Login | `/login.html` | API key authentication |
| Dashboard | `/dashboard.html` | Overview of credits, usage, applications |
| Applications | `/applications.html` | Install and manage applications |
| API Keys | `/credentials.html` | Create and revoke API credentials |
| Usage | `/usage.html` | View AI usage statistics and costs |
| Credits | `/billing.html` | Manage credit balance and transactions |
| Knowledge | `/knowledge.html` | Manage knowledge spaces and documents |
| Logs | `/logs.html` | View audit events |

## Files Structure

```
frontend/
├── css/
│   └── styles.css       # Main stylesheet with SaaS design system
├── js/
│   ├── api.js           # API client for Platform REST APIs
│   └── app.js           # Application logic and page handlers
├── login.html           # Authentication page
├── dashboard.html       # Main dashboard
├── applications.html    # Applications management
├── credentials.html     # API keys management
├── billing.html         # Credits and billing
├── usage.html           # Usage analytics
├── knowledge.html       # Knowledge foundation
└── logs.html            # Audit logs
```

## API Integration

The frontend uses the `SimorghAPI` class (`js/api.js`) to communicate with the backend:

```javascript
const api = new SimorghAPI();

// Authentication
await api.login(apiKey);

// Applications
const apps = await api.getApplications();
await api.installApplication('shora');

// Credentials
const keys = await api.getCredentials();
await api.revokeCredential(keyId);

// Usage
const usage = await api.getUsage({ start_date, end_date });

// Billing
const account = await api.getCreditAccount();
const transactions = await api.getTransactions();

// Knowledge
const spaces = await api.getKnowledgeSpaces();
await api.createKnowledgeSpace({ name, description });
const docs = await api.getDocuments(spaceId);

// Audit
const events = await api.getAuditEvents();
```

## Authentication

Authentication is handled via API keys stored in `localStorage`:

1. User enters API key on login page
2. Key is validated by making a test request to `/api/v1/applications`
3. On success, key is stored in `localStorage` as `simorgh_api_key`
4. All subsequent requests include `Authorization: Bearer <key>` header
5. Logout clears the stored key

## Styling

The CSS uses a design system with CSS custom properties:

- Clean, modern SaaS aesthetic
- Responsive layout (sidebar + main content)
- Reusable components: cards, tables, forms, modals, badges
- Color scheme: Blue primary, semantic colors for status

## Usage

### Development

Serve the frontend directory with any static file server:

```bash
# Python
cd frontend
python -m http.server 8080

# Node.js
npx serve frontend
```

Then open `http://localhost:8080/login.html` in your browser.

### Production

Build/deploy the static files to your web server or CDN.

Configure the API base URL if different from same-origin:

```javascript
// In js/api.js or inline script
const api = new SimorghAPI('https://api.yourplatform.com/api/v1');
```

## Security Notes

- API keys are stored in browser localStorage
- Keys should have appropriate scopes limiting their access
- HTTPS is required in production
- Keys are never displayed in full (only prefix shown)
- Revoked keys immediately lose access

## Browser Support

Modern browsers with ES6+ support:
- Chrome 80+
- Firefox 75+
- Safari 13+
- Edge 80+

## Future Enhancements

Potential additions while maintaining architecture principles:

- Chart.js integration for usage visualization
- WebSocket support for real-time updates
- PWA capabilities for offline access
- Dark mode toggle
- Multi-language support (i18n)
- Enhanced document upload UI with progress
