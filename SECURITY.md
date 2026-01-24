# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in Rustfava, please report it through
GitHub's private vulnerability reporting:

1. Go to the [Security Advisories](https://github.com/rustledger/rustfava/security/advisories) page
2. Click "Report a vulnerability"
3. Provide details about the vulnerability

We will respond within 48 hours and work with you to address the issue.

Please do not open public issues for security vulnerabilities.

## Security Best Practices

### Production Deployment

When deploying Rustfava in production, consider the following security headers:

```python
# Example Flask middleware for security headers
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response
```

### Reverse Proxy Configuration

For production deployments behind a reverse proxy (nginx, Caddy, etc.):

- Use HTTPS with valid certificates
- Set appropriate `Content-Security-Policy` headers
- Enable HSTS (HTTP Strict Transport Security)
- Restrict access to trusted networks if handling sensitive financial data

### Environment Variables

Never commit sensitive data. Use environment variables for:

- API keys and tokens
- Database credentials
- Secret keys for session management

## Automated Security Scanning

This repository uses:

- **Dependabot**: Automated dependency updates for security patches
- **CodeQL**: Static analysis for Python and JavaScript vulnerabilities
