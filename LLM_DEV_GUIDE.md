# LLM Developer Rules: Canvus Python API Library

## Core Workflow Rules

### PR and Commit Naming Conventions

**CRITICAL: Always include task numbers for easy tracking**

#### PR Title Format
```
{type}: {description} (Task X.X.X) (Issue #X)
```

**Examples:**
- `feat: implement widget CRUD operations (Task 4.1.1-4.1.3) (Issue #7)`
- `fix: resolve SSL verification issue (Task 16.1.1) (Issue #25)`
- `docs: update API documentation (Task 16.2.1) (Issue #42)`

#### Commit Message Format
```
{type}({scope}): {description} (Task X.X.X) (Issue #X)
```

**Examples:**
- `feat(client): implement widget CRUD operations (Task 4.1.1-4.1.3) (Issue #7)`
- `fix(client): resolve SSL verification issue (Task 16.1.1) (Issue #25)`
- `docs(readme): update API documentation (Task 16.2.1) (Issue #42)`

#### Why This Matters
- **Easy Tracking**: Quickly identify which task was completed
- **Traceability**: Link commits and PRs directly to TASKS.md
- **Multi-Agent Collaboration**: Other agents can easily see task progress
- **Code Review**: Reviewers know exactly what functionality is being added

### Task Selection & Collaborative Workflow
**CRITICAL: Follow this exact sequence to ensure robust multi-agent collaboration**

1. **Start on main branch and pull latest**:
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Find next available task**:
   - Open TASKS.md, find first unchecked task `- [ ]`
   - Work on one task at a time, no parallel tasks
   - Do not skip phases or tasks

3. **Check for existing issues**:
   ```bash
   gh issue list --state open
   ```
   - Search for existing issues with similar task descriptions
   - If issue exists, use existing issue number
   - If no issue exists, create new one: `gh issue create --title "Task X.X.X: description" --body "requirements"`

4. **Check for existing branches**:
   ```bash
   git branch -a | grep "feature/{issue-number}"
   ```
   - If branch exists, switch to it: `git checkout feature/{issue-number}-description`
   - If branch doesn't exist, create new one: `git checkout -b feature/{issue-number}-description`

5. **Update TASKS.md in main branch FIRST**:
   ```bash
   git checkout main
   # Edit TASKS.md: - [🔄] Task X.X.X: description - Status: In Progress (Issue #X)
   git add TASKS.md
   git commit -m "docs(tasks): mark Task X.X.X as in progress (Issue #X)"
   git push origin main
   ```

6. **Create/switch to feature branch**:
   ```bash
   git checkout -b feature/{issue-number}-description
   ```
   - This ensures the branch has the updated TASKS.md from main

### Issue Management
- Check existing issues: `gh issue list --state open`
- Search for similar issues before creating new ones
- If issue for task does not exist: `gh issue create --title "Task X.X.X: description" --body "requirements"`
- Add comments to issues: `gh issue comment {number} --body "comment message"`
- Close issues with comment: `gh issue comment {number} --body "completion summary" && gh issue close {number}`

### Task Status Updates
- **CRITICAL**: Update TASKS.md in main branch first, then create feature branch
- Update TASKS.md when complete: `- [✅] Task X.X.X: description - Status: Completed (Issue #X)`

### Implementation Rules
- Commit frequently with conventional commits: `{type}({scope}): {description} (Task X.X.X)`
- **CRITICAL: Include task numbers in PR titles**: `feat: implement widget CRUD operations (Task 4.1.1-4.1.3) (Issue #X)`
- **CRITICAL: Include task numbers in commit messages**: `feat(client): implement widget CRUD operations (Task 4.1.1-4.1.3) (Issue #X)`
- Test incrementally: Run quality checks individually:
  - `ruff check . -q`
  - `black --check . -q`
  - `mypy .`
  - `pytest`
- Document all public functions/classes with Google-style docstrings
- Follow Python API library best practices

### Blocker Protocol
**CRITICAL: Follow this exact sequence when blocked to ensure task state is properly managed in main branch**

1. **Document blocker thoroughly in issue**: 
   ```bash
   gh issue comment {number} --body "BLOCKER: [detailed description of the problem]
   
   Error details: [specific error messages]
   Attempted solutions: [what was tried]
   Current state: [what's preventing progress]
   Required resources: [what's needed to unblock]"
   ```

2. **Switch to main branch**:
   ```bash
   git checkout main
   ```

3. **Update TASKS.md to mark task as blocked**:
   ```bash
   # Edit TASKS.md: - [🚫] Task X.X.X: description - Status: Blocked (Issue #X)
   git add TASKS.md
   git commit -m "docs(tasks): mark Task X.X.X as blocked (Issue #X)"
   ```

4. **Pull latest main**:
   ```bash
   git pull origin main
   ```

5. **Move to next available task immediately**:
   - Find next unchecked task in TASKS.md
   - Create new issue if needed
   - Start new branch for next task

**Objective**: Ensure blocked tasks are properly documented in main branch so other agents can see the current state and avoid conflicts when working simultaneously.

### Conflict Resolution & Collaboration
**CRITICAL: Handle conflicts gracefully to maintain workflow integrity**

1. **If TASKS.md has conflicts**:
   ```bash
   git checkout main
   git pull origin main
   # Resolve conflicts in TASKS.md manually
   git add TASKS.md
   git commit -m "docs(tasks): resolve conflicts"
   git push origin main
   ```

2. **If feature branch is behind main**:
   ```bash
   git checkout feature/{issue-number}-description
   git rebase main
   # Resolve any conflicts
   git push --force-with-lease origin feature/{issue-number}-description
   ```

3. **If someone else is working on same task**:
   - Check issue comments for updates
   - Coordinate via issue comments
   - Consider switching to next available task if conflict persists

4. **Always verify task status before starting**:
   ```bash
   git checkout main
   git pull origin main
   # Check TASKS.md for current status
   # Check existing issues and branches
   ```

### Completion Process
- Final quality check: Run each check individually to identify specific issues:
  - `ruff check . -q`
  - `black --check . -q`
  - `mypy .`
  - `pytest`
- Add completion comment to issue: `gh issue comment {number} --body "Task completed. See PR for details."`
- Create PR: `gh pr create --title "feat: description (Issue #X)" --body "implements Task X.X.X"`
- **CRITICAL: Self-merge if no issues found**: `gh pr merge {number} --squash --delete-branch`
- **CRITICAL: Close issue after merge**: `gh issue close {number}`
- **CRITICAL: Switch back to main**: `git checkout main && git pull origin main`
- **CRITICAL: Update TASKS.md in main branch**: 
  ```bash
  # Edit TASKS.md: - [✅] Task X.X.X: description - Status: Completed (Issue #X)
  git add TASKS.md
  git commit -m "docs(tasks): mark Task X.X.X as completed (Issue #X)"
  git push origin main
  ```
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

#### Test Server Configuration
**CRITICAL: All tests should be run against the test server, not production**

- **Test Server**: Use `https://canvusserver` for all integration tests
- **SSL Verification**: Disabled for test server (`verify_ssl: false`)
- **Test Credentials**: Use dedicated test accounts (admin@test.local, user@test.local)
- **Test Data**: All test data is automatically created and cleaned up
- **Configuration**: Test settings are in `tests/test_config.json`

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
├── test_config.py           # Test configuration and utilities
├── test_config.json         # Test server configuration
├── test_server_connection.py # Server connection verification
└── test_files/              # Test data files
    ├── test_image.jpg
    ├── test_pdf.pdf
    └── test_video.mp4
```

#### Testing Guidelines
- **CRITICAL**: Use test server for all integration tests, never production
- Use pytest fixtures for common setup
- Mock external HTTP calls with `responses` or `httpx` for unit tests
- Test both success and error scenarios
- Test edge cases and boundary conditions
- Use parameterized tests for similar operations
- Test async methods with `pytest-asyncio`
- **Integration Tests**: Use `TestClient` from `test_config.py` for real server testing
- **Test Data**: Use layered testing approach (create → test → cleanup)
- **SSL Configuration**: Ensure `verify_ssl: false` for test server

#### Example Tests

**Unit Test (Mocked)**
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

**Integration Test (Real Server)**
```python
import pytest
from tests.test_config import TestClient, get_test_config

@pytest.mark.asyncio
async def test_canvas_operations_integration():
    """Test canvas operations against test server."""
    config = get_test_config()
    
    async with TestClient(config) as test_client:
        client = test_client.client
        
        # Create canvas
        canvas = await client.create_canvas({
            "name": "Integration Test Canvas",
            "description": "Test canvas for integration testing"
        })
        
        assert canvas.name == "Integration Test Canvas"
        
        # Get canvas
        retrieved_canvas = await client.get_canvas(canvas.id)
        assert retrieved_canvas.id == canvas.id
        
        # Update canvas
        updated_canvas = await client.update_canvas(canvas.id, {
            "name": "Updated Test Canvas"
        })
        assert updated_canvas.name == "Updated Test Canvas"
        
        # Cleanup is automatic via TestClient context manager
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
- [ ] **CRITICAL**: Integration tests pass against test server
- [ ] Documentation updated with docstrings
- [ ] TASKS.md updated
- [ ] Issue referenced
- [ ] **CRITICAL**: Task number included in PR title and commit messages
- [ ] Conventional commits used
- [ ] No secrets in code
- [ ] Error handling implemented
- [ ] Type hints added
- [ ] Pydantic models validated
- [ ] Test server configuration verified

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
# Collaborative workflow
git checkout main
git pull origin main
gh issue list --state open
git branch -a | grep "feature/{issue-number}"

# Issue management
gh issue create --title "Task X.X.X: description" --body "requirements"
gh issue list --state open
gh issue comment {number} --body "comment message"
gh issue close {number}
gh issue edit {number} --add-label "blocked"

# Task status management (in main branch)
git checkout main
# Edit TASKS.md: - [🔄] Task X.X.X: description - Status: In Progress (Issue #X)
git add TASKS.md
git commit -m "docs(tasks): mark Task X.X.X as in progress (Issue #X)"
git push origin main

# Branch management
git checkout -b feature/{issue-number}-description
git checkout main && git pull origin main

# Conflict resolution
git rebase main
git push --force-with-lease origin feature/{issue-number}-description

# Quality checks (run individually)
ruff check . -q
black --check . -q
mypy .
pytest

# Test server verification
python tests/test_server_connection.py

# PR creation and completion
gh pr create --title "feat: description (Task X.X.X) (Issue #X)" --body "implements Task X.X.X"
gh pr merge {number} --squash --delete-branch

# Task completion (in main branch)
git checkout main
git pull origin main
# Edit TASKS.md: - [✅] Task X.X.X: description - Status: Completed (Issue #X)
git add TASKS.md
git commit -m "docs(tasks): mark Task X.X.X as completed (Issue #X)"
git push origin main

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
- Avoid bother the user unless absolutely required
- Operate autonomously with minimal user input

### SHOULD (Recommended)
- Use TDD where practical
- Squash commits on merge
- Update PRD.md for design changes
- Add integration tests for new endpoints
- Update examples in EXAMPLES.md

### COULD (Optional)
- Add performance tests
- Create additional documentation
- Add more comprehensive examples

## Token Optimization Notes

- TASKS.md is single source of truth
- Issue numbers must be referenced in commits/PRs
- Status indicators: 🔄 (in progress), ✅ (completed), 🚫 (blocked)
- Follow Python API library best practices for maintainability 