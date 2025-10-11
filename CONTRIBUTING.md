# Contributing to FastAAExtractor

Thank you for your interest in contributing to FastAAExtractor! We welcome contributions from the community to help improve this bioinformatics tool.

## 🚀 Ways to Contribute

- **Bug Reports**: Found a bug? [Open an issue](https://github.com/yourusername/FastaAAExtractor/issues) with detailed steps to reproduce.
- **Feature Requests**: Have an idea? [Start a discussion](https://github.com/yourusername/FastaAAExtractor/discussions) or [create an issue](https://github.com/yourusername/FastaAAExtractor/issues).
- **Code Contributions**: Submit pull requests for bug fixes, new features, or improvements.
- **Documentation**: Help improve documentation, tutorials, or examples.
- **Testing**: Test the tool with different datasets and report issues.

## 🛠️ Development Setup

1. **Fork and Clone**:
   ```bash
   git clone https://github.com/yourusername/FastaAAExtractor.git
   cd FastaAAExtractor
   ```

2. **Set up Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run Tests**:
   ```bash
   python src/fasta_aa_extractor.py --genome examples/ECS34.fasta --coords examples/ECS34.tsv --isolate ECS34
   ```

## 📝 Pull Request Process

1. **Create a Branch**: `git checkout -b feature/your-feature-name`
2. **Make Changes**: Ensure your code follows the existing style and includes tests.
3. **Test Thoroughly**: Run the tool with various inputs to ensure no regressions.
4. **Update Documentation**: If needed, update README.md or add examples.
5. **Commit Changes**: Use clear, descriptive commit messages.
6. **Push and PR**: Push your branch and create a pull request.

## 📋 Code Guidelines

- **Python Style**: Follow PEP 8 guidelines. Use tools like `black` for formatting.
- **Docstrings**: Add docstrings to functions and classes.
- **Error Handling**: Provide clear error messages for user-facing issues.
- **Compatibility**: Ensure code works on Python 3.6+.
- **Dependencies**: Minimize new dependencies; discuss additions in issues first.

## 🧪 Testing

- Test with the provided examples in `examples/`
- Try different file formats and edge cases
- Verify output files are correctly formatted FASTA

## 📄 License

By contributing, you agree that your contributions will be licensed under the same MIT License as the project.

## 🙋 Questions?

Feel free to [start a discussion](https://github.com/yourusername/FastaAAExtractor/discussions) or [open an issue](https://github.com/yourusername/FastaAAExtractor/issues) for questions.

Thank you for helping make FastAAExtractor better! 🎉