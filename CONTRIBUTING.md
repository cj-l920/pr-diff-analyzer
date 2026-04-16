## Contributing

We love contributions! Here's how you can help make PR Diff Analyzer better:

### Ways to Contribute

- 🐛 **Report bugs** - Open an issue with detailed reproduction steps
- 💡 **Suggest features** - Share your ideas for new detection patterns or integrations
- 📝 **Improve documentation** - Fix typos, clarify instructions, add examples
- 🔧 **Submit code** - Fix bugs or add new features

### Development Setup

```bash
# Clone the repository
git clone https://github.com/cj-l920/pr-diff-analyzer.git
cd pr-diff-analyzer

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Run tests
pytest

# Run linter
flake8 pr_analyzer.py

# Format code
black pr_analyzer.py
```

### Submitting Changes

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Make your changes with clear, focused commits
4. Add tests for new functionality
5. Ensure all tests pass: `pytest`
6. Update documentation as needed
7. Push to your fork: `git push origin feature/my-feature`
8. Open a Pull Request with a clear description

### Adding New Security Patterns

To add a new security detection pattern:

1. Add the regex pattern to `DiffAnalyzer.SECURITY_PATTERNS`
2. Add a description to the README.md security table
3. Add a test case to verify the pattern works
4. Update the CHANGELOG.md

### Code Style

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for classes and functions
- Keep functions focused and modular

### Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Focus on the code, not the person
- Help newcomers learn and grow

Thank you for contributing! 🚀