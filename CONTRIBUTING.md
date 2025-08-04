# Contributing to Athens Real Estate Analysis

Thank you for your interest in contributing to this research project! This guide will help you understand how to contribute effectively.

## 🎯 Project Overview

This project analyzes the correlation between property size (SQM) and energy efficiency in Athens real estate market. We welcome contributions that improve the analysis, add new features, or enhance the methodology.

## 🤝 Ways to Contribute

### 1. 🐛 Bug Reports
- **Search existing issues** before creating new ones
- **Provide detailed reproduction steps**
- **Include error messages and logs**
- **Specify your environment** (Python version, OS, etc.)

### 2. 💡 Feature Requests
- **Explain the problem** you're trying to solve
- **Describe your proposed solution**
- **Consider implementation complexity**
- **Discuss potential impact** on existing functionality

### 3. 📊 Data Improvements
- **New data sources** for validation
- **Additional neighborhoods** or cities
- **Data quality enhancements**
- **Validation methodology improvements**

### 4. 🔬 Analysis Enhancements
- **New statistical methods**
- **Additional correlation analyses**
- **Visualization improvements**
- **Investment intelligence features**

## 🛠️ Development Setup

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Git for version control
git --version
```

### Installation
```bash
# Clone the repository
git clone https://github.com/chrimar3/spitogatos-premium-analysis.git
cd spitogatos-premium-analysis

# Install dependencies
pip install -r requirements.txt

# Run basic analysis to verify setup
python analyzers/sqm_energy_correlation_analyzer.py
```

### Development Dependencies
```bash
# Install additional development tools
pip install pytest black flake8 mypy jupyter
```

## 📝 Code Style Guidelines

### Python Code Style
- **Follow PEP 8** style guidelines
- **Use meaningful variable names**
- **Add docstrings** to all functions and classes
- **Include type hints** where appropriate
- **Limit line length** to 88 characters (Black formatter)

### Example Function Format
```python
def analyze_energy_correlation(df: pd.DataFrame, confidence_level: float = 0.95) -> Dict[str, float]:
    """
    Calculate correlation between property size and energy efficiency.
    
    Args:
        df: DataFrame containing property data with 'sqm' and 'energy_class' columns
        confidence_level: Statistical confidence level for analysis (default: 0.95)
    
    Returns:
        Dictionary containing correlation coefficients and p-values
        
    Raises:
        ValueError: If required columns are missing from DataFrame
    """
    # Implementation here
    pass
```

### Data Analysis Guidelines
- **Validate all input data** before analysis
- **Include confidence intervals** for statistical results
- **Document assumptions** and limitations
- **Preserve data provenance** (source, timestamp, extraction method)

## 🔍 Testing Guidelines

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_analyzers.py

# Run with coverage report
python -m pytest --cov=. tests/
```

### Writing Tests
- **Test all public functions**
- **Include edge cases** and error conditions
- **Use descriptive test names**
- **Mock external dependencies** (web scraping, file I/O)

### Example Test
```python
def test_energy_correlation_calculation():
    """Test correlation calculation with known data."""
    # Arrange
    test_data = pd.DataFrame({
        'sqm': [50, 100, 150],
        'energy_class': ['C', 'B', 'A']
    })
    
    # Act
    result = analyze_energy_correlation(test_data)
    
    # Assert
    assert 'correlation' in result
    assert -1 <= result['correlation'] <= 1
    assert 'p_value' in result
```

## 📊 Data Contribution Guidelines

### Data Quality Standards
- **Authenticity**: All data must be from real, verifiable sources
- **Completeness**: Core fields (price, sqm, energy_class) must be present
- **Accuracy**: Data should reflect current market conditions
- **Provenance**: Include source URL and extraction timestamp

### Adding New Data Sources
1. **Document the source** (platform, URL, access method)
2. **Create extraction script** following existing patterns
3. **Implement validation** for data quality
4. **Add tests** for the new data pipeline
5. **Update documentation** with new source details

### Data Privacy
- **No personal information** (owner names, contact details)
- **Aggregate data only** for public analysis
- **Respect platform terms of service**
- **Follow ethical scraping practices**

## 🔬 Analysis Contribution Guidelines

### Statistical Rigor
- **Use appropriate statistical methods** for the data type
- **Report confidence intervals** for all estimates
- **Test for statistical significance**
- **Document methodological choices**

### Reproducibility Requirements
- **Include all code** for analysis
- **Document random seeds** for reproducible results
- **Provide sample data** for testing
- **Version control all changes**

### New Analysis Types
1. **Propose the analysis** in an issue first
2. **Discuss methodology** with maintainers
3. **Implement with tests** and documentation
4. **Validate results** against existing analyses

## 📋 Pull Request Process

### Before Submitting
- [ ] **Run all tests** and ensure they pass
- [ ] **Update documentation** for any new features
- [ ] **Add tests** for new functionality
- [ ] **Follow code style** guidelines
- [ ] **Update CHANGELOG.md** if applicable

### Pull Request Template
```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Analysis Impact
- [ ] No impact on existing analysis results
- [ ] Results may change (explain why)
- [ ] New analysis capabilities added

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

### Review Process
1. **Automated checks** must pass (GitHub Actions)
2. **Code review** by project maintainers
3. **Analysis validation** for statistical changes
4. **Documentation review** for completeness
5. **Merge** after approval

## 📚 Documentation Contributions

### Types of Documentation
- **Code documentation** (docstrings, comments)
- **Analysis methodology** (statistical approaches)
- **User guides** (how to run analyses)
- **API documentation** (function references)

### Documentation Standards
- **Clear and concise** explanations
- **Include examples** where helpful
- **Keep up to date** with code changes
- **Use proper markdown** formatting

## 🚨 Issue Reporting

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug.

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS 12.0]
- Python version: [e.g., 3.9.7]
- Package versions: [paste requirements.txt or pip freeze output]

## Additional Context
Any other relevant information.
```

### Feature Request Template
```markdown
## Feature Description
Clear description of the proposed feature.

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches you've thought about.

## Implementation Notes
Technical considerations or constraints.
```

## 🏆 Recognition

### Contributors
All contributors will be:
- **Listed in CONTRIBUTORS.md**
- **Credited in commit messages**
- **Acknowledged in release notes**
- **Invited to co-author academic papers** (for significant contributions)

### Academic Collaboration
For substantial research contributions:
- **Co-authorship opportunities** on academic publications
- **Conference presentation** opportunities
- **Research collaboration** on related projects

## 📞 Getting Help

### Communication Channels
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For general questions and ideas
- **Pull Request Comments**: For code-specific discussions

### Response Times
- **Bug reports**: 24-48 hours for initial response
- **Feature requests**: 1-2 weeks for evaluation
- **Pull requests**: 3-5 days for initial review

## 📄 License

By contributing to this project, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

**Thank you for contributing to advancing real estate market analysis through data science!**

🤖 *This project uses AI-assisted development with human oversight to ensure quality and accuracy.*