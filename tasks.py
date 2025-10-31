from invoke import task


@task(
    help={"part": "Part of the version to bump: major, minor, patch (default: patch)"}
)
def bump(c, part="patch"):
    """Bump version using uv version and create a git tag."""
    result = c.run("git status --short", hide=True)
    if result.stdout != "":
        print("Working directory is not clean. Please commit or stash changes first.")
        return
    c.run(f"uv version --bump {part}")
    c.run("uv lock")
    c.run("git add pyproject.toml uv.lock")
    new_version = c.run("uv version --short", hide=True).stdout.strip()
    c.run(f'git commit -m "{new_version}"')
    c.run(f"git tag -a v{new_version} -m '{new_version}'")


@task
def format(c):
    c.run("uv run ruff check --fix src")
    c.run("uv run ruff format src")


@task
def dev(c, build=False):
    c.run(f"docker compose up {'--build' if build else ''} --watch", pty=True)


@task
def import_dump(
    c,
    file_name="data_dump.json",
    download_dir="/tmp/db-data",
    bucket_path="django-dump",
):
    """Import dump from S3 and load it into the database."""
    c.run(
        f"docker compose exec wagtail uv run command.py import-dump -f {file_name} -d {download_dir} -b {bucket_path}"
    )


@task
def export_dump(
    c,
    output_dir="/tmp/db-data",
    file_name="data_dump.json",
    bucket_path="django-dump",
    local=False,
    no_timestamp=False,
):
    """Dump database and export dump to S3."""
    c.run(
        f"docker compose exec wagtail uv run command.py export-dump -o {output_dir} -f {file_name} -b {bucket_path} {'-l' if local else ''} {'-n' if no_timestamp else ''}"
    )
