# Contributing

Thanks for your interest in contributing to Hide and Seek. This project is student-centered and learning-friendly. We welcome contributions of all sizes, from typo fixes to new features.

## Ways to contribute
- Bug fixes and improvements
- UI/UX enhancements and accessibility upgrades
- Documentation, examples, and onboarding guides
- Testing and quality improvements

If you are new to open source, feel free to ask questions. We are happy to help.

## Code of Conduct
By participating, you agree to follow `CODE_OF_CONDUCT.md`.

## Getting started
### 1) Fork and clone
Create a fork, then clone your fork locally.

### 2) Backend setup
```bash
cd backend
python -m pip install --upgrade pip
python -m pip install uv
uv venv
uv sync
uv run uvicorn app.main:app --reload
```

Create `backend/.env` based on the README configuration. The backend defaults to `http://localhost:8000`.

### 3) Frontend setup
```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and proxies `/api` to the backend.

## Development notes
- **Dev login** is available only when `DEBUG=true` in `backend/.env`.
- Avoid using real student data in local or shared environments.
- Make accessibility a priority (keyboard navigation, contrast, clear labels).

## Branches and commits
- Create a feature branch from `main`.
- Keep commits focused and descriptive.

Example:
```
feat: add team invite banner
fix: handle empty event list
```

## Pull requests
Please include:
- A short summary of the change and the user impact
- Screenshots for UI changes
- Any new configuration or migration notes

We aim to review PRs with a teaching mindset: constructive feedback and clear rationale.

## Testing
Automated tests are not yet set up. If you add tests, include instructions for running them. If your change is test-sensitive, describe how you verified it.

## Style and quality
- Keep code readable and well-organized.
- Prefer small, composable components and functions.
- Update documentation when behavior or configuration changes.

## Security
If you discover a vulnerability, do not open a public issue. See `SECURITY.md`.

## License
By contributing, you agree that your contributions will be licensed under `LICENSE.md`.
