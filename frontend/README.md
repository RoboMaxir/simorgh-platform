# SIMORGH Platform Frontend

Lightweight vanilla HTML/CSS/JavaScript infrastructure dashboard.

## Runtime

Serve the frontend from the same origin as the FastAPI application when possible. API base defaults to /api/v1. A deployment may set window.SIMORGH_CONFIG.API_BASE_URL before application scripts load.

## Authentication

Human users authenticate through POST /api/v1/auth/login. The access token is stored in sessionStorage for the SPA session. Theme preference is the only item stored in localStorage. The machine-to-machine POST /api/v1/auth/token flow is not used for dashboard login.

## Architecture

state.js holds session/theme state. api/client.js owns transport and error handling. api/*.js owns endpoint adapters. components are presentational. pages load API data and bind it to components. No fake production metrics are used.

## Known backend limitation

The human login token currently lacks the tenant/application/scope context required by the protected AI, knowledge and audit dependencies. This frontend reports those calls as unavailable rather than inventing context or data.

Applications, credential CRUD, billing and user/workspace management remain UI shells because matching backend routes were not verified in the target branch.
