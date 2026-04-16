# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability in this project, please report it responsibly:

1. **DO NOT** open a public issue
2. Email the maintainer directly or open a private security advisory on GitHub
3. Allow reasonable time for a fix before public disclosure

## Security Considerations

This tool analyzes code for security issues, but also has security implications:

### API Tokens
- Store `GITHUB_TOKEN` and `OPENAI_API_KEY` securely
- Use environment variables or secret management systems
- Never commit tokens to version control
- Use tokens with minimum required permissions

### Code Analysis
- The tool sends code diffs to OpenAI for analysis (if enabled)
- Be aware of data privacy implications when analyzing proprietary code
- Consider using local LLM models for sensitive codebases

### GitHub Actions
- The provided workflow uses `secrets.GITHUB_TOKEN` which is automatically provided
- Ensure workflow permissions are set correctly in your repository settings

## Best Practices

1. Regularly rotate API keys
2. Review AI-generated suggestions before acting on them
3. Use this tool as part of a comprehensive security strategy
4. Keep the tool updated to benefit from new detection patterns