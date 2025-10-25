# 🤝 Contributing to JARVIS AI Assistant

First off, thank you for considering contributing to JARVIS! It's people like you that make JARVIS such a great tool.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Plugin Development](#plugin-development)

## Code of Conduct

This project and everyone participating in it is governed by our commitment to foster an open and welcoming environment. By participating, you are expected to uphold this standard.

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR-USERNAME/PROJECT_JARVIS_3.0.git`
3. Add upstream remote: `git remote add upstream https://github.com/ORIGINAL-OWNER/PROJECT_JARVIS_3.0.git`

## Development Setup

### Prerequisites
- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 20+ (for frontend development)
- Make (optional, for convenience commands)

### Local Development

```bash
# Setup environment
python setup.py

# Start only database and Redis
make dev

# Backend development
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development (in another terminal)
cd frontend
npm install
npm run dev
```

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment details (OS, Docker version, etc.)

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- A clear and descriptive title
- A detailed description of the proposed feature
- Why this enhancement would be useful
- Possible implementation approach

### Your First Code Contribution

Unsure where to begin? Look for issues tagged with:
- `good first issue` - simple issues for newcomers
- `help wanted` - issues that need assistance

## Pull Request Process

1. **Create a branch**: `git checkout -b feature/YourFeatureName`

2. **Make your changes**:
   - Write clean, documented code
   - Follow coding standards (see below)
   - Add tests for new features
   - Update documentation

3. **Test your changes**:
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend lint
   cd frontend
   npm run lint
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```
   
   Use conventional commits:
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `style:` - Code style changes (formatting, etc.)
   - `refactor:` - Code refactoring
   - `test:` - Adding or updating tests
   - `chore:` - Maintenance tasks

5. **Push to your fork**:
   ```bash
   git push origin feature/YourFeatureName
   ```

6. **Open a Pull Request**:
   - Fill in the PR template
   - Link any related issues
   - Request review from maintainers

7. **Address review feedback**:
   - Make requested changes
   - Push additional commits
   - Re-request review

## Coding Standards

### Python (Backend)

- Follow PEP 8
- Use type hints
- Write docstrings for functions/classes
- Keep functions small and focused
- Use async/await properly

```python
async def example_function(param: str) -> Dict[str, Any]:
    """
    Brief description of function.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    """
    # Implementation
    return {"result": "value"}
```

### TypeScript (Frontend)

- Use TypeScript strict mode
- Define interfaces for data structures
- Use functional components with hooks
- Follow React best practices

```typescript
interface ExampleProps {
  data: string
  onAction: () => void
}

const ExampleComponent: React.FC<ExampleProps> = ({ data, onAction }) => {
  // Implementation
  return <div>{data}</div>
}
```

### General

- Write meaningful commit messages
- Keep PRs focused on a single feature/fix
- Update tests and documentation
- Ensure CI passes before requesting review

## Plugin Development

To create a new plugin:

1. **Create plugin file** in `backend/app/plugins/`:
   ```python
   from app.core.plugin_manager import PluginBase
   from typing import Dict, Any
   
   class MyPlugin(PluginBase):
       name = "my_plugin"
       version = "1.0.0"
       description = "My awesome plugin"
       author = "Your Name"
       
       async def initialize(self) -> bool:
           # Setup code
           return True
       
       async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
           # Plugin logic
           return {"result": "processed"}
       
       async def shutdown(self):
           # Cleanup code
           pass
   ```

2. **Test your plugin**:
   ```python
   # In backend/tests/test_my_plugin.py
   import pytest
   from app.plugins.my_plugin import MyPlugin
   
   @pytest.mark.asyncio
   async def test_my_plugin():
       plugin = MyPlugin()
       await plugin.initialize()
       result = await plugin.process({"input": "test"})
       assert "result" in result
   ```

3. **Document your plugin** in README.md

## Questions?

Feel free to open an issue with the `question` label or reach out to the maintainers.

---

**Thank you for contributing to JARVIS! 🤖✨**

