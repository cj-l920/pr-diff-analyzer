# PR Diff Analysis Agent

An intelligent code review agent that analyzes GitHub Pull Request diffs for security issues, breaking changes, test coverage, and provides AI-powered summaries.

## 🎯 Features

- **Security Scanning**: Detects hardcoded secrets, SQL injection risks, eval usage, and more
- **Breaking Change Detection**: Identifies API changes, function removals, and database migrations
- **Test Coverage Analysis**: Calculates test-to-source ratios and provides recommendations
- **AI-Powered Insights**: Uses OpenAI GPT-4 for intelligent PR summaries
- **Multiple Output Formats**: JSON, Markdown, or human-readable summary
- **GitHub Action Integration**: Automatically comment on PRs with analysis results

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/pr-diff-analyzer.git
cd pr-diff-analyzer

# Install dependencies
pip install requests

# Set environment variables
export GITHUB_TOKEN="your_github_token"
export OPENAI_API_KEY="your_openai_key"  # Optional, for AI analysis
```

### Basic Usage

```bash
# Analyze a PR
python pr_analyzer.py --owner facebook --repo react --pr 12345

# Post analysis as PR comment
python pr_analyzer.py --owner facebook --repo react --pr 12345 --post-comment

# Output as JSON
python pr_analyzer.py --owner facebook --repo react --pr 12345 --output json
```

## 📋 Requirements

- Python 3.8+
- GitHub Personal Access Token (with `repo` scope)
- OpenAI API Key (optional, for AI features)

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GITHUB_TOKEN` | Yes | GitHub Personal Access Token |
| `OPENAI_API_KEY` | No | OpenAI API Key for AI analysis |

### Command Line Options

```
usage: pr_analyzer.py [-h] --owner OWNER --repo REPO --pr PR 
                      [--github-token GITHUB_TOKEN] [--openai-key OPENAI_KEY]
                      [--post-comment] [--output {json,markdown,summary}]
                      [--github-base-url GITHUB_BASE_URL]

options:
  -h, --help            show this help message and exit
  --owner OWNER         Repository owner (user or organization)
  --repo REPO           Repository name
  --pr PR               Pull request number
  --github-token TOKEN  GitHub personal access token
  --openai-key KEY      OpenAI API key for AI analysis
  --post-comment        Post analysis as a comment on the PR
  --output FORMAT       Output format: json, markdown, summary
  --github-base-url URL GitHub API base URL (for GitHub Enterprise)
```

## 🔒 Security Detection

The analyzer detects the following security patterns:

| Pattern | Description |
|---------|-------------|
| `hardcoded_secret` | Passwords, tokens, or API keys in code |
| `sql_injection` | Dynamic SQL query construction |
| `eval_usage` | Use of dangerous eval() functions |
| `dangerous_deserialization` | Unsafe pickle/yaml loading |
| `insecure_http` | Hardcoded HTTP URLs (should use HTTPS) |

## ⚠️ Breaking Change Detection

Identifies potential breaking changes:

- Function/method removals
- Class removals
- API endpoint changes
- Database migrations (DROP/ALTER operations)

## 🧪 Test Coverage Analysis

Calculates:
- Test files changed vs source files
- Test lines added vs source lines added
- Coverage ratio recommendations

## 🤖 AI Analysis

When OpenAI API key is provided, the agent generates:
- PR summary (what the changes do)
- Complexity assessment (Low/Medium/High)
- Risk level evaluation
- Key changes identification
- Improvement recommendations

## 📊 Output Example

### Summary Output

```
============================================================
📊 PR Analysis Summary
============================================================
PR: #12345 - Add user authentication middleware
Author: @johndoe
Files Changed: 12
Additions: +456
Deletions: -123

📝 Summary:
This PR introduces a new authentication middleware that validates JWT tokens 
for protected routes. It includes token refresh logic and error handling.

🚨 Security Concerns: 1
⚠️ Breaking Changes: 0

💡 Suggestions: 3
🧪 Test Coverage: Add tests

✅ Comment posted to PR #12345
```

### JSON Output

```json
{
  "pr_number": 12345,
  "pr_title": "Add user authentication middleware",
  "author": "johndoe",
  "summary": "This PR introduces a new authentication middleware...",
  "files_changed": 12,
  "additions": 456,
  "deletions": 123,
  "issues": [
    {
      "type": "security",
      "items": [...]
    }
  ],
  "suggestions": [...],
  "security_concerns": [...],
  "test_coverage": {
    "test_files_changed": 2,
    "source_files_changed": 10,
    "coverage_ratio": 0.3,
    "recommendation": "Add tests"
  },
  "breaking_changes": [],
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## 🔄 GitHub Actions Integration

Add the provided workflow to `.github/workflows/pr-analysis.yml` in your repository:

```yaml
name: PR Diff Analysis
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install requests
      - name: Run PR Analysis
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          python pr_analyzer.py \
            --owner ${{ github.repository_owner }} \
            --repo ${{ github.event.repository.name }} \
            --pr ${{ github.event.pull_request.number }} \
            --post-comment
```

## 🏢 GitHub Enterprise Support

For GitHub Enterprise Server:

```bash
python pr_analyzer.py \
  --owner my-org \
  --repo my-repo \
  --pr 42 \
  --github-base-url https://github.mycompany.com/api/v3
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a PR with your changes

## 📧 Support

For issues and feature requests, please use the GitHub issue tracker.
