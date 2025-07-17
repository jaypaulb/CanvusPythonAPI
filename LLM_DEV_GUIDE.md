# LLM Developer Rules: Canvus Python API Library

## Core Workflow Rules

### Task Selection
- Open TASKS.md, find first unchecked task `- [ ]`
- Work on one task at a time, no parallel tasks
- Do not skip phases or tasks
- Follow the implementation roadmap in PRD.md

### Issue Management
- Check existing issues: `gh issue list`
- Create issue before any work: `gh issue create --title "Task X.X.X: description" --body "requirements"`
- Note issue number, create branch: `git checkout -b feature/{issue-number}-description`
- Add comments to issues: `gh issue comment {number} --body "comment message"`
- Close issues with comment: `gh issue comment {number} --body "completion summary" && gh issue close {number}`

### Task Status Updates
- Update TASKS.md immediately when starting: `- [🔄] Task X.X.X: description - Status: In Progress (Issue #X)`
- Commit status change: `git commit -m "docs(tasks): mark Task X.X.X as in progress (Issue #X)"`
- Update TASKS.md when complete: `- [✅] Task X.X.X: description - Status: Completed (Issue #X)`

### Implementation Rules
- Commit frequently with conventional commits: `{type}({scope}): {description}`
- Test incrementally: Run quality checks individually:
  - `ruff check .`
  - `black --check .`
  - `mypy .`
  - `pytest`
- Document all public functions/classes with Google-style docstrings
- Follow Python API library best practices

### Blocker Protocol
- Document blocker in issue: `gh issue comment {number} --body "blocker details"`
- Mark issue with labels: `gh issue edit {number} --add-label "blocked"`
- Update TASKS.md: `- [🚫] Task X.X.X: description - Status: Blocked (Issue #X)`
- Move to next available task immediately

### Completion Process
- Final quality check: Run each check individually to identify specific issues:
  - `ruff check .`
  - `black --check .`
  - `mypy .`
  - `pytest`
- Add completion comment to issue: `gh issue comment {number} --body "Task completed. See PR for details."`
- Update TASKS.md as completed
- Create PR: `gh pr create --title "feat: description (Issue #X)" --body "implements Task X.X.X"`
- **CRITICAL: Self-merge if no issues found**: `gh pr merge {number} --squash --delete-branch`
- **CRITICAL: Close issue after merge**: `gh issue close {number}`
- **CRITICAL: Switch back to main**: `git checkout main && git pull origin main`
- Verify completion: Check PR status and issue closure

## Python API Library Best Practices

### Package Structure
```
canvus_api/
├── __init__.py          # Main client export
├── client.py            # Main client class
├── models.py            # Pydantic models
├── exceptions.py        # Custom exceptions
├── services/            # Service layer (optional)
│   ├── __init__.py
│   ├── canvas_service.py
│   ├── user_service.py
│   └── content_service.py
└── utils/               # Utility functions
    ├── __init__.py
    ├── validation.py
    └── helpers.py
```

### Code Standards

#### Quality Requirements
- All code must pass: ruff, black, mypy, pytest
- Test coverage >80%
- Conventional commits only: `{type}({scope}): {description}`
- No secrets in code
- Comprehensive error handling with custom exceptions
- Type hints for all public methods

#### Documentation Requirements
- Google-style docstrings for all public functions/classes
- Include parameter types, return types, and examples
- Update API docs for endpoint changes
- Update TASKS.md for all status changes
- Maintain comprehensive README.md and EXAMPLES.md

#### Security Rules
- Use environment variables for configuration
- Validate all inputs with Pydantic models
- Handle errors gracefully with custom exception hierarchy
- No sensitive data in logs
- Secure credential handling

### API Design Principles

#### Method Naming Convention
```python
# Resource-based naming for CRUD operations
client.list_canvases()
client.get_canvas(canvas_id)
client.create_canvas(payload)
client.update_canvas(canvas_id, payload)
client.delete_canvas(canvas_id)

# Action-based naming for special operations
client.move_canvas(canvas_id, folder_id)
client.copy_canvas(canvas_id, payload)
client.upload_file(canvas_id, file_path)
```

#### Parameter Design
```python
# Required parameters as positional arguments
client.get_canvas(canvas_id)

# Optional parameters as keyword arguments
client.list_canvases(subscribe=True, limit=100)

# Complex data as dictionaries or Pydantic models
client.create_canvas({
    "name": "My Canvas",
    "folder_id": "folder-123"
})
```

#### Return Types
```python
# Single resources return Pydantic models
canvas: Canvas = client.get_canvas(canvas_id)

# Lists return List[PydanticModel]
canvases: List[Canvas] = client.list_canvases()

# Binary data returns bytes
image_data: bytes = client.download_image(canvas_id, image_id)

# Streaming returns AsyncGenerator
async for update in client.subscribe_widgets(canvas_id):
    print(update)
```

### Error Handling Strategy

#### Exception Hierarchy
```python
class CanvusAPIError(Exception):
    """Base exception for all Canvus API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None, response_text: Optional[str] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text

class AuthenticationError(CanvusAPIError):
    """Authentication and authorization errors."""
    pass

class ValidationError(CanvusAPIError):
    """Input validation errors."""
    pass

class ResourceNotFoundError(CanvusAPIError):
    """Resource not found errors."""
    pass

class RateLimitError(CanvusAPIError):
    """Rate limiting errors."""
    pass
```

### Testing Best Practices

#### Test Structure
```
tests/
├── __init__.py
├── conftest.py              # Pytest fixtures
├── test_client.py           # Main client tests
├── test_models.py           # Model validation tests
├── test_services/           # Service layer tests
│   ├── test_canvas_service.py
│   ├── test_user_service.py
│   └── test_content_service.py
├── test_integration.py      # Integration tests
└── test_files/              # Test data files
    ├── test_image.jpg
    ├── test_pdf.pdf
    └── test_video.mp4
```

#### Testing Guidelines
- Use pytest fixtures for common setup
- Mock external HTTP calls with `responses` or `httpx`
- Test both success and error scenarios
- Test edge cases and boundary conditions
- Use parameterized tests for similar operations
- Test async methods with `pytest-asyncio`

#### Example Test
```python
import pytest
from unittest.mock import AsyncMock
from canvus_api import CanvusClient, Canvas

@pytest.mark.asyncio
async def test_get_canvas_success():
    """Test successful canvas retrieval."""
    client = CanvusClient("https://test.com", "token")
    client._request = AsyncMock(return_value={
        "id": "canvas-123",
        "name": "Test Canvas",
        "folder_id": "folder-123"
    })
    
    canvas = await client.get_canvas("canvas-123")
    
    assert isinstance(canvas, Canvas)
    assert canvas.id == "canvas-123"
    assert canvas.name == "Test Canvas"
```

### Documentation Best Practices

#### Docstring Format (Google Style)
```python
async def create_canvas(self, payload: Dict[str, Any]) -> Canvas:
    """Create a new canvas.
    
    Args:
        payload: Canvas creation data containing name and optional folder_id.
            Must include 'name' field. 'folder_id' is optional.
            
    Returns:
        Canvas: The created canvas object.
        
    Raises:
        ValidationError: If payload is missing required fields.
        AuthenticationError: If authentication fails.
        CanvusAPIError: For other API-related errors.
        
    Example:
        >>> canvas = await client.create_canvas({
        ...     "name": "My Project",
        ...     "folder_id": "folder-123"
        ... })
        >>> print(canvas.name)
        My Project
    """
```

#### README Structure
- Installation instructions
- Quick start guide with examples
- API reference with common operations
- Error handling examples
- Contributing guidelines
- License information

### Release Management

#### Version Management
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Update version in `pyproject.toml`
- Create release notes for each version
- Tag releases in GitHub

#### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch: `git checkout -b release/v1.2.0`
4. Run full test suite
5. Create release PR
6. Merge and tag: `git tag v1.2.0 && git push origin v1.2.0`
7. Create GitHub release with release notes

## Communication Rules

### Blocker Communication
- Document thoroughly in issue comments
- Include error messages, attempted solutions
- Tag relevant team members if needed
- Move to next task after documenting

### Issue Updates
- Comment on issues for progress updates
- Include completion checklists
- Reference related tasks in TASKS.md

## Emergency Procedures

### Work Loss
- Check `git status` and `git log`
- Look for uncommitted changes
- Contact team immediately

### Breaking Changes
- Document what happened in issue
- Create new branch for fix
- Do not attempt complex fixes alone
- Follow semantic versioning for breaking changes

## Success Criteria

### Before PR Submission
- [ ] Code passes quality checks
- [ ] Tests pass with >80% coverage
- [ ] Documentation updated with docstrings
- [ ] TASKS.md updated
- [ ] Issue referenced
- [ ] Conventional commits used
- [ ] No secrets in code
- [ ] Error handling implemented
- [ ] Type hints added
- [ ] Pydantic models validated

### Task Completion
- [ ] Implementation working
- [ ] Quality checks pass
- [ ] Issue updated
- [ ] TASKS.md updated
- [ ] PR created and reviewed
- [ ] **CRITICAL: PR self-merged (if no issues)**
- [ ] **CRITICAL: Issue closed**
- [ ] **CRITICAL: Switched back to main branch**
- [ ] **CRITICAL: Latest changes pulled**

## Commands Reference

```bash
# Issue management
gh issue create --title "Task X.X.X: description" --body "requirements"
gh issue list
gh issue comment {number} --body "comment message"
gh issue close {number}
gh issue edit {number} --add-label "blocked"

# Branch management
git checkout -b feature/{issue-number}-description
git checkout main && git pull origin main

# Quality checks (run individually)
ruff check .
black --check .
mypy .
pytest

# PR creation and completion
gh pr create --title "feat: description (Issue #X)" --body "implements Task X.X.X"
gh pr merge {number} --squash --delete-branch

# Release management
git tag v1.2.0
git push origin v1.2.0
gh release create v1.2.0 --title "Release v1.2.0" --notes "Release notes"
```

## Rule Enforcement

### MUST (Blocking)
- Update TASKS.md for all status changes
- Create issue before any work
- Use conventional commits
- Pass all quality checks
- Include tests for new code
- Document public code with Google-style docstrings
- Handle blockers per protocol
- Use type hints for all public methods
- Validate inputs with Pydantic models

### SHOULD (Recommended)
- Use TDD where practical
- Squash commits on merge
- Update PRD.md for design changes
- Add integration tests for new endpoints
- Update examples in EXAMPLES.md

### COULD (Optional)
- Use chat for quick questions
- Add performance tests
- Create additional documentation
- Add more comprehensive examples

## Token Optimization Notes

- TASKS.md is single source of truth
- Issue numbers must be referenced in commits/PRs
- Status indicators: 🔄 (in progress), ✅ (completed), 🚫 (blocked)
- Move to next task immediately when blocked
- Document thoroughly, then continue working
- Follow Python API library best practices for maintainability 