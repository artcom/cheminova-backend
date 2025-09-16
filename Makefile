.PHONY: format bump-patch

# Format the repository using ruff (fix + formatter)
format:
	uv run ruff check --fix .
	uv run ruff format .

# Bump patch version (e.g. 2.0.6 -> 2.0.7), commit, and tag
bump-patch:
	uv version --bump patch
	ver=$$(uv version --short); \
	git add pyproject.toml uv.lock; \
	git commit -m "chore: bump version to $$ver"; \
	git tag v$$ver
	@echo "Bumped to $$ver (tag v$$ver)"
	@echo "Push with: git push origin main --tags"
