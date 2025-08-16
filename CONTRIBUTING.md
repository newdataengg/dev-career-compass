# 🤝 Contributing to DevCareerCompass

Thank you for your interest in contributing to DevCareerCompass! This document provides guidelines and information for contributors.

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style Guidelines](#code-style-guidelines)
4. [Testing Guidelines](#testing-guidelines)
5. [Pull Request Process](#pull-request-process)
6. [Feature Development](#feature-development)
7. [Bug Reports](#bug-reports)
8. [Documentation](#documentation)
9. [Community Guidelines](#community-guidelines)

## 🚀 Getting Started

### Prerequisites

- **Python 3.8+**
- **Git**
- **Qdrant Cloud Account** (free tier available)
- **GitHub account**

### Quick Start

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/dev-career-compass.git
   cd dev-career-compass
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv ai-cap
   source ai-cap/bin/activate  # Windows: ai-cap\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp env.example .env
   
   # Edit .env with your configuration
   # At minimum, set your GitHub token
   ```

4. **Initialize database**
   ```bash
   python -c "from src.database.connection import init_database; init_database()"
   ```

5. **Setup Qdrant Cloud** (optional, for vector search)
   ```bash
   # Follow QDRANT_CLOUD_SETUP.md for cloud setup
   python qdrant_cloud_setup.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## 🛠️ Development Setup

### Project Structure

```
dev-career-compass/
├── 📁 src/                          # Core source code
│   ├── 🗄️ database/                # Database models & connection
│   ├── 🔍 vector_store/            # Qdrant Cloud vector database client
│   ├── 🤖 agents/                  # Multi-agent system
│   ├── 🧠 llm/                     # LLM integration
│   ├── 🔗 embeddings/              # Vector embedding generation
│   ├── 🌐 knowledge_graph/         # Graph RAG implementation
│   ├── 📊 insights/                # Career analysis engine
│   ├── ⚙️ config/                  # Configuration management
│   └── 🛠️ utils/                   # Utility functions
├── 🌐 templates/                    # Web application templates
├── 🎨 static/                       # CSS, JS, and assets
├── 🧪 tests/                        # Test suite
├── ☁️ QDRANT_CLOUD_SETUP.md        # Qdrant Cloud setup guide
├── 🔑 API_KEYS_SETUP.md            # API keys setup guide
└── 📊 real_data_collector.py       # Multi-platform data collection
```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the code style guidelines
   - Add tests for new functionality
   - Update documentation

3. **Test your changes**
   ```bash
   # Run all tests
   python -m pytest tests/
   
   # Run specific test file
   python -m pytest tests/test_your_feature.py
   
   # Check project status
   python project_status.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template

## 📝 Code Style Guidelines

### Python Code Style

We follow **PEP 8** guidelines with some additional requirements:

#### General Rules
- **Line length**: Maximum 88 characters (Black formatter)
- **Indentation**: 4 spaces (no tabs)
- **Imports**: Grouped and sorted (isort)
- **Type hints**: Required for all function parameters and return values
- **Docstrings**: Required for all public functions and classes

#### Example Code
```python
from typing import List, Dict, Optional, Any
import logging
from datetime import datetime

from src.utils.logger import get_application_logger

logger = get_application_logger(__name__)


class ExampleClass:
    """Example class demonstrating code style guidelines."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the example class.
        
        Args:
            name: The name of the instance
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.created_at = datetime.utcnow()
    
    def process_data(self, data: List[str]) -> Dict[str, int]:
        """Process a list of strings and return character counts.
        
        Args:
            data: List of strings to process
            
        Returns:
            Dictionary mapping strings to their character counts
            
        Raises:
            ValueError: If data is empty
        """
        if not data:
            raise ValueError("Data cannot be empty")
        
        logger.info(f"Processing {len(data)} items")
        
        result = {}
        for item in data:
            result[item] = len(item)
        
        return result
```

#### Import Order
```python
# Standard library imports
import os
import sys
from datetime import datetime
from typing import List, Dict

# Third-party imports
import numpy as np
import requests
from flask import Flask, jsonify

# Local application imports
from src.config.settings import settings
from src.utils.logger import get_application_logger
```

### JavaScript/HTML/CSS Style

#### JavaScript
- Use **ES6+** features
- Prefer `const` and `let` over `var`
- Use arrow functions where appropriate
- Add JSDoc comments for functions

#### HTML
- Use semantic HTML5 elements
- Include proper accessibility attributes
- Keep templates clean and readable

#### CSS
- Use **BEM** methodology for class naming
- Prefer CSS Grid and Flexbox over floats
- Use CSS custom properties for theming

## 🧪 Testing Guidelines

### Test Structure

```
tests/
├── unit/                    # Unit tests
│   ├── test_database.py
│   ├── test_vector_store.py
│   └── test_agents.py
├── integration/             # Integration tests
│   ├── test_api.py
│   └── test_workflows.py
└── fixtures/                # Test data and fixtures
    ├── sample_data.json
    └── mock_responses.py
```

### Writing Tests

#### Unit Tests
```python
import pytest
from unittest.mock import Mock, patch
from src.vector_store.qdrant_client import QdrantVectorClient


class TestQdrantClient:
    """Test cases for QdrantVectorClient."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = QdrantVectorClient()
    
    def test_connection_success(self):
        """Test successful connection to Qdrant Cloud."""
        with patch('qdrant_client.QdrantClient') as mock_client:
            mock_client.return_value = Mock()
            
            result = self.client.health_check()
            
            assert result is not None
            mock_client.assert_called_once()
    
    def test_search_similar_skills(self):
        """Test skill similarity search."""
        # Arrange
        query_vector = [0.1] * 384
        expected_results = [
            {"skill_name": "Python", "score": 0.95},
            {"skill_name": "JavaScript", "score": 0.87}
        ]
        
        with patch.object(self.client, 'client') as mock_client:
            mock_client.search.return_value = expected_results
            
            # Act
            results = self.client.search_similar_skills(query_vector, top_k=2)
            
            # Assert
            assert results == expected_results
            mock_client.search.assert_called_once()
```

#### Integration Tests
```python
import pytest
from flask.testing import FlaskClient
from app import app


class TestAPIEndpoints:
    """Integration tests for API endpoints."""
    
    @pytest.fixture
    def client(self) -> FlaskClient:
        """Create test client."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    def test_get_statistics(self, client: FlaskClient):
        """Test statistics endpoint."""
        response = client.get('/api/statistics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'developers' in data
        assert 'repositories' in data
        assert 'skills' in data
    
    def test_analyze_developer(self, client: FlaskClient):
        """Test developer analysis endpoint."""
        data = {"username": "testuser"}
        response = client.post('/api/analyze', json=data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'developer' in data
        assert 'career_analysis' in data
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run specific test file
python -m pytest tests/test_vector_store.py

# Run tests with verbose output
python -m pytest -v

# Run tests in parallel
python -m pytest -n auto
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage required
- **API endpoints**: 100% coverage required

## 🔄 Pull Request Process

### PR Template

When creating a pull request, use the following template:

```markdown
## Description
Brief description of the changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Code coverage meets requirements

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings generated
- [ ] All tests pass

## Screenshots (if applicable)
Add screenshots for UI changes.

## Additional Notes
Any additional information or context.
```

### Review Process

1. **Automated Checks**
   - Code style (Black, isort, flake8)
   - Type checking (mypy)
   - Test coverage
   - Security scanning

2. **Manual Review**
   - Code quality and logic
   - Performance implications
   - Security considerations
   - Documentation quality

3. **Approval Requirements**
   - At least one maintainer approval
   - All automated checks pass
   - No merge conflicts

## 🚀 Feature Development

### Feature Request Process

1. **Create an issue**
   - Use the "Feature Request" template
   - Provide detailed description
   - Include use cases and examples

2. **Discussion**
   - Gather community feedback
   - Define requirements
   - Plan implementation approach

3. **Implementation**
   - Create feature branch
   - Implement with tests
   - Update documentation

4. **Review and Merge**
   - Submit PR for review
   - Address feedback
   - Merge after approval

### Feature Guidelines

#### New Vector Collections
```python
def create_new_collection(self, dimension: int = 768) -> Collection:
    """Create new vector collection following project standards."""
    collection_name = "new_vectors"
    
    # Define schema
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="entity_id", dtype=DataType.INT64),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=255),
        FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=dimension),
        FieldSchema(name="metadata", dtype=DataType.JSON)
    ]
    
    schema = CollectionSchema(fields=fields, description="New vector collection")
    collection = Collection(name=collection_name, schema=schema)
    
    # Create index
    index_params = {
        "metric_type": "COSINE",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="vector", index_params=index_params)
    
    return collection
```

#### New API Endpoints
```python
@app.route('/api/new_endpoint', methods=['POST'])
@login_required
def new_endpoint():
    """New API endpoint following project standards."""
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Process request
        result = process_request(data)
        
        # Log success
        logger.info(f"Successfully processed request: {result}")
        
        return jsonify(result), 200
        
    except ValueError as e:
        logger.warning(f"Invalid request: {e}")
        return jsonify({"error": str(e)}), 400
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500
```

## 🐛 Bug Reports

### Bug Report Template

```markdown
## Bug Description
Clear and concise description of the bug.

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

## Expected Behavior
What you expected to happen.

## Actual Behavior
What actually happened.

## Environment
- OS: [e.g. macOS, Windows, Linux]
- Python Version: [e.g. 3.9.7]
- Browser: [e.g. Chrome, Firefox] (if applicable)
- DevCareerCompass Version: [e.g. 1.0.0]

## Additional Context
- Screenshots
- Error logs
- Console output
```

### Bug Fix Process

1. **Reproduce the bug**
   - Confirm the issue exists
   - Create minimal reproduction case

2. **Investigate**
   - Check logs and error messages
   - Review related code
   - Identify root cause

3. **Fix**
   - Implement the fix
   - Add tests to prevent regression
   - Update documentation if needed

4. **Test**
   - Verify the fix works
   - Ensure no new issues introduced
   - Run full test suite

## 📚 Documentation

### Documentation Standards

#### Code Documentation
- **Docstrings**: Use Google style docstrings
- **Type hints**: Required for all public APIs
- **Comments**: Explain complex logic, not obvious code

#### User Documentation
- **README.md**: Project overview and quick start
- **DOCUMENTATION.md**: Technical details and API reference
- **Inline comments**: Explain complex business logic

#### Example Documentation
```python
def analyze_career_path(
    user_skills: List[str],
    target_role: str,
    experience_years: int
) -> Dict[str, Any]:
    """Analyze career path and provide recommendations.
    
    This function analyzes a user's current skills against a target role
    to provide personalized career recommendations and skill gap analysis.
    
    Args:
        user_skills: List of skills the user currently possesses
        target_role: The desired career role to analyze
        experience_years: Years of professional experience
        
    Returns:
        Dictionary containing:
            - career_prediction: Predicted career trajectory
            - skill_gaps: Skills needed for target role
            - recommendations: Learning recommendations
            - confidence_score: Analysis confidence (0-1)
            
    Raises:
        ValueError: If user_skills is empty or target_role is invalid
        CareerAnalysisError: If analysis fails due to insufficient data
        
    Example:
        >>> result = analyze_career_path(
        ...     ["Python", "SQL"],
        ...     "Data Scientist",
        ...     2
        ... )
        >>> print(result["skill_gaps"])
        ["Machine Learning", "Statistics", "R"]
    """
```

### Documentation Updates

When making changes that affect documentation:

1. **Update relevant docs**
   - README.md for user-facing changes
   - DOCUMENTATION.md for technical changes
   - Code comments for implementation details

2. **Review documentation**
   - Ensure accuracy and completeness
   - Check for broken links
   - Verify code examples work

3. **Test documentation**
   - Run code examples
   - Verify installation instructions
   - Check API documentation

## 👥 Community Guidelines

### Code of Conduct

We are committed to providing a welcoming and inclusive environment for all contributors. Please:

- **Be respectful** and considerate of others
- **Be collaborative** and open to feedback
- **Be constructive** in criticism and suggestions
- **Be inclusive** and welcoming to new contributors

### Communication

- **Issues**: Use GitHub issues for bug reports and feature requests
- **Discussions**: Use GitHub Discussions for questions and ideas
- **Pull Requests**: Use PR comments for code review and feedback

### Recognition

Contributors will be recognized in:
- **README.md**: Contributors section
- **Release notes**: For significant contributions
- **GitHub**: Contributor statistics and activity

### Getting Help

- **Documentation**: Check README.md and DOCUMENTATION.md first
- **Issues**: Search existing issues for similar problems
- **Discussions**: Ask questions in GitHub Discussions
- **Community**: Join our community channels

## 🎯 Contribution Areas

### High Priority
- **Performance optimization**: Vector search improvements
- **New data sources**: Additional career data integration
- **UI/UX improvements**: Better user experience
- **Testing**: Increased test coverage

### Medium Priority
- **New features**: Additional analysis capabilities
- **Documentation**: Improved guides and examples
- **Monitoring**: Better observability and logging
- **Security**: Security improvements and audits

### Low Priority
- **Nice-to-have features**: Additional visualizations
- **Code cleanup**: Refactoring and optimization
- **Tooling**: Development tool improvements

## 📞 Contact

- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and community discussion
- **Email**: For security issues or private matters

---

Thank you for contributing to DevCareerCompass! 🚀 