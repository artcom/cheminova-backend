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
def test(c):
    """Run tests using django test framework."""
    c.run("docker compose exec wagtail uv run manage.py test")


@task
def import_dump(
    c,
    file_name,
    download_dir="/tmp/db-data",
    bucket_path="db-dump",
    s3_alias="dev-cheminova",
    bucket_name="dev-cheminova",
):
    """Import dump from S3 and load it into the database."""
    c.run(
        f"docker compose exec wagtail uv run manage.py import_dump "
        f"{file_name} "
        f"-d {download_dir} "
        f"-b {bucket_path} "
        f"-a {s3_alias} "
        f"-n {bucket_name}",
        pty=True,
    )


@task
def export_dump(
    c,
    output_dir="/tmp/db-data",
    file_name="data_dump.json",
    s3_alias="local-cheminova",
    bucket_name="local-cheminova",
    bucket_path="db-export",
    local=False,
):
    """Dump database and export dump to S3."""
    c.run(
        f"docker compose exec wagtail uv run manage.py export_dump "
        f"-o {output_dir} "
        f"-f {file_name} "
        f"-b {bucket_path} "
        f"-a {s3_alias} "
        f"-n {bucket_name} "
        f"{'-l' if local else ''}",
        pty=True,
    )


@task
def sync_assets(
    c,
    s3_alias="dev-cheminova",
    bucket_name="dev-cheminova",
    bucket_path="media",
    media_path="/app/media",
    remove=False,
    overwrite=False,
):
    """Sync static and media assets from S3 to local storage."""
    c.run(
        f"docker compose exec wagtail uv run manage.py sync_assets "
        f"-a {s3_alias} "
        f"-n {bucket_name} "
        f"-b {bucket_path} "
        f"-m {media_path} "
        f"{'-r' if remove else ''} "
        f"{'-o' if overwrite else ''}",
        pty=True,
    )
