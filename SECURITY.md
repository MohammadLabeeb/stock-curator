# Security Policy

## Supported Versions

We take security seriously. Currently, we support:

| Version | Supported          |
| ------- | ------------------ |
| Latest  | :white_check_mark: |

## Security Best Practices

### 1. API Key Management

**DO:**
- ✅ Store API keys in environment variables (`.env` file)
- ✅ Use the `.env.example` file as a template
- ✅ Add `.env` to `.gitignore` (already configured)
- ✅ Use GitHub Secrets for CI/CD workflows
- ✅ Rotate API keys regularly

**DON'T:**
- ❌ Never commit `.env` files to version control
- ❌ Never hardcode API keys in source code
- ❌ Never share API keys in public channels
- ❌ Never log API keys or tokens

### 2. Environment Variables

The following API keys are required:

- `WORLD_NEWS_API_KEY` - For news scraping
- `GEMINI_API_KEY` - For LLM extraction
- `UPSTOX_ACCESS_TOKEN` - For stock data fetching

**Setup:**
```bash
cp .env.example .env
# Edit .env and add your actual API keys
```

### 3. GitHub Actions Secrets

When deploying with GitHub Actions, ensure these secrets are configured:

1. Go to: Repository Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `WORLD_NEWS_API_KEY`
   - `GEMINI_API_KEY`
   - `UPSTOX_ACCESS_TOKEN`

### 4. Dependency Security

We regularly monitor dependencies for vulnerabilities:

- Dependencies are managed via `pyproject.toml` and `requirements.txt`
- Use `pip-audit` or `safety` to check for known vulnerabilities:
  ```bash
  pip install pip-audit
  pip-audit -r requirements.txt
  ```

### 5. Code Security

- No use of `eval()`, `exec()`, or unsafe dynamic code execution
- Input validation for all external data sources
- Proper error handling without exposing sensitive information
- Timeout configurations for all API calls

### 6. Data Security

- No sensitive data stored in git repository
- API responses are sanitized before logging
- Personal or financial data is never logged

## Reporting a Vulnerability

If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public GitHub issue
2. Email the repository owner at: [Create an email address or use GitHub Security Advisories]
3. Or use GitHub's private vulnerability reporting:
   - Go to the Security tab
   - Click "Report a vulnerability"
   
Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

## Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 5 business days
- **Fix Timeline**: Depends on severity
  - Critical: 24-48 hours
  - High: 1 week
  - Medium: 2 weeks
  - Low: 30 days

## Security Features

### Current Implementations

✅ **Environment Variable Protection**
- All API keys loaded from `.env` file
- `.env` excluded from version control
- Example file (`.env.example`) provided without real keys

✅ **GitHub Actions Security**
- Secrets stored in GitHub Actions environment
- No secrets in workflow YAML files
- Minimal permissions for workflow jobs

✅ **Logging Safety**
- No API keys logged
- Error messages sanitized
- Response data truncated in error logs

✅ **Input Validation**
- Stock symbols validated against NSE/BSE master list
- Date formats validated
- API response validation before processing

✅ **Network Security**
- HTTPS only for all API calls
- Request timeouts configured (10-15 seconds)
- Retry logic with backoff for failed requests

### Planned Improvements

🔄 **Dependency Scanning**
- Automated dependency vulnerability scanning
- Regular security updates

🔄 **CodeQL Analysis**
- GitHub Advanced Security scanning
- Automated security code review

## Third-Party Services

We use the following third-party services:

| Service | Purpose | Security Notes |
|---------|---------|----------------|
| World News API | News scraping | API key in environment variables |
| Google Gemini | LLM extraction | API key in environment variables |
| Upstox | Stock data | Access token in environment variables |
| GitHub Actions | CI/CD | Secrets management enabled |
| Streamlit Cloud | Dashboard hosting | Read-only data access |

## Compliance

- No PII (Personally Identifiable Information) collected
- No user authentication required
- Public data sources only
- Read-only operations on financial data APIs

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security.html)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

## Changelog

### 2025-12-23
- Initial security policy created
- Documented API key management practices
- Added vulnerability reporting guidelines
