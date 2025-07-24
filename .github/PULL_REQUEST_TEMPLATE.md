# Pull Request

## Description

Brief description of what this PR does.

## Type of Change

- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Dependency update

## Related Issues

Fixes # (issue number)
Closes # (issue number)
Relates to # (issue number)

## Changes Made

### Backend Changes
- [ ] Models
- [ ] Views/API endpoints
- [ ] Serializers
- [ ] Tests
- [ ] Database migrations
- [ ] Celery tasks
- [ ] Other: _______________

### Frontend Changes
- [ ] Components
- [ ] Pages
- [ ] Hooks
- [ ] State management
- [ ] Styling
- [ ] Tests
- [ ] Other: _______________

### Infrastructure Changes
- [ ] Docker configuration
- [ ] CI/CD pipeline
- [ ] Environment configuration
- [ ] Documentation
- [ ] Other: _______________

## How Has This Been Tested?

- [ ] Unit tests
- [ ] Integration tests
- [ ] End-to-end tests
- [ ] Manual testing
- [ ] Performance testing

**Test Configuration:**
- OS: [e.g. macOS, Ubuntu]
- Python Version: [e.g. 3.11]
- Node Version: [e.g. 18]
- Browser: [e.g. Chrome 119]

## Screenshots (if applicable)

| Before | After |
|--------|-------|
| ![before](url) | ![after](url) |

## Checklist

### Code Quality
- [ ] My code follows the project's coding standards
- [ ] I have performed a self-review of my own code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

### Security
- [ ] I have checked for security vulnerabilities
- [ ] Sensitive data is properly handled
- [ ] Authentication and authorization are correctly implemented
- [ ] Input validation is in place
- [ ] No hardcoded secrets or credentials

### Performance
- [ ] I have considered the performance impact of my changes
- [ ] Database queries are optimized
- [ ] No N+1 query problems introduced
- [ ] Large operations are handled asynchronously if needed

### Database
- [ ] Database migrations are included and tested
- [ ] Migrations are reversible
- [ ] No data loss in migrations
- [ ] Indexes are added where necessary

### API Changes
- [ ] API changes are backward compatible OR properly versioned
- [ ] API documentation is updated
- [ ] Swagger/OpenAPI schema is updated
- [ ] Response formats are consistent

### UI/UX (if applicable)
- [ ] UI is responsive and works on mobile devices
- [ ] Accessibility guidelines are followed
- [ ] Error states are handled gracefully
- [ ] Loading states are implemented
- [ ] User feedback is provided for actions

## Deployment Notes

### Environment Variables
List any new environment variables that need to be set:
- `NEW_VAR_NAME`: Description of what it does

### Database Migrations
- [ ] This PR includes database migrations
- [ ] Migrations have been tested on a copy of production data
- [ ] Migration rollback plan is documented

### Third-party Dependencies
- [ ] New dependencies are necessary and well-maintained
- [ ] Dependencies are properly licensed
- [ ] Security audit of new dependencies is complete

### Configuration Changes
List any configuration changes required:
- Docker environment
- Nginx/Caddy configuration
- CI/CD pipeline changes

## Rollback Plan

If this change needs to be rolled back:
1. Step 1
2. Step 2
3. Step 3

## Additional Notes

Any additional information that reviewers should know.

## Reviewer Guidelines

Please ensure you've reviewed:
- [ ] Code logic and implementation
- [ ] Test coverage and quality
- [ ] Documentation updates
- [ ] Security implications
- [ ] Performance impact
- [ ] Database migration safety
- [ ] API compatibility
- [ ] UI/UX consistency (if applicable)

---

**Note for Reviewers:** Please use GitHub's review features to provide feedback and suggestions. For major architectural changes, consider requesting a design review meeting. 