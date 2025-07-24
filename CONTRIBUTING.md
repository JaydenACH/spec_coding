# Contributing to Respond IO Alternate Interface

Thank you for your interest in contributing to this project! This document provides guidelines and information for contributors.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contributing Process](#contributing-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Documentation](#documentation)
- [Security](#security)

## Code of Conduct

This project adheres to a code of conduct that ensures a welcoming environment for everyone. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

### Prerequisites

- **Docker & Docker Compose** (recommended for development)
- **Python 3.11+** (for backend development)
- **Node.js 18+** (for frontend development)
- **Git** for version control

### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/your-username/respond-io-alternate.git
   cd respond-io-alternate
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start development environment**
   ```bash
   make dev
   # OR
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/api/docs/

## Contributing Process

1. **Create an issue** (for bugs or feature requests)
2. **Fork the repository** to your GitHub account
3. **Create a feature branch** from `develop`
4. **Make your changes** following our coding standards
5. **Write or update tests** for your changes
6. **Test your changes** locally
7. **Commit your changes** with descriptive messages
8. **Push to your fork** and create a pull request
9. **Respond to review feedback** promptly

### Branch Naming Convention

- `feature/short-description` - for new features
- `bugfix/issue-number-description` - for bug fixes
- `hotfix/critical-issue` - for critical production fixes
- `docs/improvement-description` - for documentation updates
- `refactor/component-name` - for code refactoring

## Coding Standards

### Python (Backend)

We use Python 3.11+ with Django 4.2+ and follow PEP 8 guidelines.

**Code Formatting:**
```bash
# Format code
make format

# Check formatting
black --check backend/
isort --check-only backend/
flake8 backend/
```

**Standards:**
- Use type hints where possible
- Follow Django best practices
- Write docstrings for public functions/classes
- Maximum line length: 88 characters (Black default)
- Use meaningful variable and function names

**Example:**
```python
from typing import Optional
from django.db import models


class Customer(models.Model):
    """Customer model representing WhatsApp contacts."""
    
    name: str = models.CharField(max_length=100)
    
    def get_display_name(self) -> str:
        """Return customer display name."""
        return self.name or self.phone_number
```

### TypeScript/React (Frontend)

We use TypeScript with strict mode and follow modern React patterns.

**Code Formatting:**
```bash
# Format code
make format-frontend

# Check formatting and linting
npm run lint
npm run type-check
npx prettier --check .
```

**Standards:**
- Use functional components with hooks
- Implement proper TypeScript types
- Follow React best practices
- Use Tailwind CSS for styling
- Implement proper error boundaries

**Example:**
```typescript
interface CustomerListProps {
  customers: Customer[];
  onSelectCustomer: (customer: Customer) => void;
}

export const CustomerList: React.FC<CustomerListProps> = ({
  customers,
  onSelectCustomer,
}) => {
  return (
    <div className="space-y-2">
      {customers.map((customer) => (
        <CustomerCard
          key={customer.id}
          customer={customer}
          onClick={() => onSelectCustomer(customer)}
        />
      ))}
    </div>
  );
};
```

### Database

**Migration Guidelines:**
- Always create reversible migrations
- Test migrations on a copy of production data
- Never delete columns directly (deprecate first)
- Add indexes for frequently queried fields

**Model Guidelines:**
- Use UUID primary keys for security
- Add proper indexes for performance
- Include comprehensive help_text
- Implement model validation in `clean()` methods

## Testing Guidelines

### Backend Testing

We use pytest for backend testing with comprehensive coverage.

**Test Structure:**
```
backend/
├── tests/
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_views.py
│   │   └── test_serializers.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   └── test_respond_io_integration.py
│   └── fixtures/
│       └── sample_data.json
```

**Running Tests:**
```bash
# Run all backend tests
make test

# Run with coverage
make test-coverage

# Run specific test
cd backend && python -m pytest tests/unit/test_models.py::TestCustomerModel
```

**Test Guidelines:**
- Write unit tests for all models and business logic
- Write integration tests for API endpoints
- Use factories for test data generation
- Mock external API calls
- Achieve minimum 90% code coverage

### Frontend Testing

We use Jest and React Testing Library for frontend testing.

**Test Structure:**
```
frontend/
├── src/
│   ├── components/
│   │   ├── CustomerList/
│   │   │   ├── CustomerList.tsx
│   │   │   └── CustomerList.test.tsx
│   └── __tests__/
│       ├── pages/
│       └── integration/
```

**Running Tests:**
```bash
# Run all frontend tests
make test-frontend

# Run with coverage
npm run test:coverage

# Run specific test
npm test CustomerList.test.tsx
```

**Test Guidelines:**
- Test component behavior, not implementation
- Test user interactions and accessibility
- Mock API calls and external dependencies
- Write integration tests for critical user flows

### End-to-End Testing

We use Playwright for E2E testing.

```bash
# Run E2E tests
make test-e2e

# Run with UI
npx playwright test --ui
```

## Commit Messages

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Format:**
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect the meaning of code
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

**Examples:**
```
feat(auth): add password reset functionality

- Implement password reset email sending
- Add reset token validation
- Update user model with reset fields

Closes #123
```

```
fix(api): resolve customer assignment race condition

The customer assignment endpoint was not properly handling
concurrent requests, causing data corruption.

Fixes #456
```

## Pull Request Process

1. **Create a descriptive PR title** following conventional commits
2. **Fill out the PR template** completely
3. **Ensure all checks pass** (CI/CD, tests, linting)
4. **Request review** from appropriate team members
5. **Address feedback** promptly and professionally
6. **Keep PR scope focused** (one feature/fix per PR)

### PR Requirements

- [ ] All tests pass
- [ ] Code coverage maintained or improved
- [ ] Documentation updated if needed
- [ ] No merge conflicts
- [ ] Follows coding standards
- [ ] Includes appropriate tests

### Review Guidelines

**For Authors:**
- Respond to feedback within 2 business days
- Ask questions if feedback is unclear
- Push additional commits to address feedback
- Use `git rebase` to clean up commit history if needed

**For Reviewers:**
- Review within 2 business days
- Provide constructive, specific feedback
- Test locally for complex changes
- Approve when satisfied with quality

## Issue Reporting

### Bug Reports

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Environment information
- Error messages and logs

### Feature Requests

Use the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:
- Clear problem statement
- Proposed solution
- User stories and acceptance criteria
- UI/UX considerations
- Technical requirements

## Documentation

### Code Documentation

- **Python**: Use docstrings following Google style
- **TypeScript**: Use JSDoc comments for complex functions
- **API**: Document all endpoints with OpenAPI/Swagger

### User Documentation

- Update README.md for setup changes
- Update API documentation for endpoint changes
- Create user guides for new features
- Update deployment documentation for infrastructure changes

### Architecture Documentation

- Document significant architectural decisions
- Update database schema documentation
- Document integration patterns
- Maintain deployment runbooks

## Security

### Reporting Security Issues

**DO NOT** open public issues for security vulnerabilities. Instead:

1. Email security findings to [security@example.com]
2. Include detailed description of the vulnerability
3. Provide steps to reproduce if possible
4. Wait for confirmation before disclosing publicly

### Security Guidelines

- Never commit secrets or credentials
- Use environment variables for configuration
- Validate all user inputs
- Implement proper authentication and authorization
- Keep dependencies updated
- Follow OWASP security guidelines

### Security Review Process

All PRs involving security-sensitive areas require:
- Security team review
- Penetration testing (for major changes)
- Dependency vulnerability scanning
- Static code analysis

## Performance Guidelines

### Backend Performance

- Use database indexes appropriately
- Implement query optimization
- Use caching where appropriate
- Monitor API response times
- Implement proper pagination

### Frontend Performance

- Optimize bundle size
- Implement code splitting
- Use image optimization
- Implement proper loading states
- Monitor Core Web Vitals

## Release Process

1. **Create release branch** from `main`
2. **Update version numbers** and changelog
3. **Test release candidate** thoroughly
4. **Create release tag** following semantic versioning
5. **Deploy to production** using automated pipeline
6. **Monitor deployment** and rollback if needed

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- MAJOR: Breaking changes
- MINOR: New features (backward compatible)
- PATCH: Bug fixes (backward compatible)

## Getting Help

- **General questions**: Open a discussion on GitHub
- **Bug reports**: Create an issue with the bug template
- **Feature requests**: Create an issue with the feature template
- **Security issues**: Email security@example.com
- **Urgent issues**: Contact the maintainers directly

## Recognition

Contributors who make significant contributions will be:
- Added to the CONTRIBUTORS.md file
- Mentioned in release notes
- Invited to join the core team (for regular contributors)

Thank you for contributing to Respond IO Alternate Interface! 🚀 