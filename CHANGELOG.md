# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-04-16

### Added
- Initial release of PR Diff Analysis Agent
- GitHub API integration for fetching PR data and diffs
- Security vulnerability scanning (5 detection patterns)
- Breaking change detection for API and database changes
- Test coverage analysis with ratio calculations
- AI-powered PR summarization using OpenAI GPT-4
- Multiple output formats: JSON, Markdown, and human-readable summary
- GitHub Actions workflow for automated PR analysis
- CLI interface with comprehensive argument parsing
- Support for GitHub Enterprise Server
- Automatic PR commenting capability

### Security Detection Patterns
- Hardcoded secrets detection
- SQL injection risk identification
- Dangerous eval() usage detection
- Unsafe deserialization pattern detection
- Insecure HTTP URL detection

### Breaking Change Detection
- Function/method removal detection
- Class removal detection
- API endpoint change identification
- Database migration operation detection

## [Unreleased]

### Planned
- Support for additional LLM providers (Anthropic Claude, Google Gemini)
- More security detection patterns (XSS, CSRF, etc.)
- Integration with SARIF format for security tools
- Custom rule configuration file support
- Web dashboard for analysis history
- Support for more programming languages