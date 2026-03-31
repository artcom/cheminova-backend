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
    """Format code using ruff."""
    c.run("uv run ruff check --fix src")
    c.run("uv run ruff format src")


@task(help={"build": "Build images before running the development server."})
def dev(c, build=False):
    """Run the development server with docker compose."""
    c.run(f"docker compose up {'--build' if build else ''} --watch", pty=True)


@task(
    help={
        "show_help": "Show help for the manage.py admin_user command. (type --show-help or -s)"
    }
)
def admin_user(
    c,
    show_help=False,
    username=None,
    password=None,
    email=None,
    first_name=None,
    last_name=None,
):
    """
    Create or update an admin user using manage.py admin_user command.
    To see all options and defaults of the manage.py admin_user command, use the --show-help option:
    uv run invoke admin-user --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py admin_user"
        f"{' --help' if show_help else ''}"
        f"{f' -u {username} ' if username else ''}"
        f"{f' -p {password} ' if password else ''}"
        f"{f' -e {email} ' if email else ''}"
        f"{f' -f {first_name} ' if first_name else ''}"
        f"{f' -l {last_name} ' if last_name else ''}",
        pty=True,
    )


@task(
    help={
        "show_help": "Show help for the manage.py init_site command. (type --show-help or -s)"
    }
)
def init_site(c, show_help=False, site_url=None):
    """
    Initialize the default Wagtail site with the given URL using manage.py init_site command.
    To see all options and defaults of the manage.py init_site command, use the --show-help option:
    uv run invoke init-site --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py init_site"
        f"{' --help' if show_help else ''}"
        f"{f' --site-url {site_url}' if site_url else ''}",
        pty=True,
    )


@task
def test(c):
    """Run tests using django test framework."""
    c.run("docker compose exec wagtail uv run manage.py test")


@task(
    help={
        "show_help": "Show help for the manage.py import_dump command. (type --show-help or -s)",
    },
)
def import_dump(
    c,
    file_name=None,
    show_help=False,
    download_dir=None,
    bucket_path=None,
    s3_alias=None,
    bucket_name=None,
    no_restore_local_data=False,
):
    """
    Import dump from S3 and load it into the database using manage.py import_dump.
    To see all options and defaults of the manage.py import_dump command, use the --show-help option:
    uv run invoke import-dump --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py import_dump"
        f"{f' {file_name}' if file_name else ''}"
        f"{' --help' if show_help else ''}"
        f"{f' --download-dir {download_dir}' if download_dir else ''}"
        f"{f' --bucket-path {bucket_path}' if bucket_path else ''}"
        f"{f' --s3-alias {s3_alias}' if s3_alias else ''}"
        f"{f' --bucket-name {bucket_name}' if bucket_name else ''}"
        f"{' --no-restore-local-data' if no_restore_local_data else ''}",
        pty=True,
    )


@task(
    help={
        "show_help": "Show help for the manage.py export_dump command. (type --show-help or -s)",
    },
)
def export_dump(
    c,
    show_help=False,
    output_dir=None,
    file_name=None,
    s3_alias=None,
    bucket_name=None,
    bucket_path=None,
    local=False,
):
    """
    Dump database and export dump to S3 using manage.py export_dump.
    To see all options and defaults of the manage.py export_dump command, use the --show-help option:
    uv run invoke export-dump --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py export_dump"
        f"{' --help' if show_help else ''}"
        f"{f' --output-dir {output_dir} ' if output_dir else ''}"
        f"{f' --file-name {file_name}' if file_name else ''}"
        f"{f' --bucket-path {bucket_path}' if bucket_path else ''}"
        f"{f' --s3-alias {s3_alias} ' if s3_alias else ''}"
        f"{f' --bucket-name {bucket_name} ' if bucket_name else ''}"
        f"{' --local' if local else ''}",
        pty=True,
    )


@task(
    help={
        "show_help": "Show help for the manage.py sync_assets command. (type --show-help or -s)",
        "to_s3": "Sync FROM local TO s3. (type --to-s3 or -t)",
    },
)
def sync_assets(
    c,
    show_help=False,
    s3_alias=None,
    bucket_name=None,
    bucket_path=None,
    media_path=None,
    remove=False,
    overwrite=False,
    to_s3=False,
):
    """
    Sync static and media assets between S3 and local storage using manage.py sync_assets command.
    To see all options and defaults of the manage.py sync_assets command, use the --show-help option:
    uv run invoke sync-assets --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py sync_assets"
        f"{' --help' if show_help else ''} "
        f"{f' --s3-alias {s3_alias}' if s3_alias else ''}"
        f"{f' --bucket-name {bucket_name}' if bucket_name else ''}"
        f"{f' --bucket-path {bucket_path}' if bucket_path else ''}"
        f"{f' --media-path {media_path}' if media_path else ''}"
        f"{' --remove' if remove else ''} "
        f"{' --overwrite' if overwrite else ''}"
        f"{' --to-s3' if to_s3 else ''}",
        pty=True,
    )


@task(
    help={
        "show_help": "Show help for the manage.py randomize_timestamps command. (type --show-help or -s)",
    },
)
def randomize_timestamps(
    c,
    character=None,
    n_days=30,
    show_help=False,
):
    """
    Randomize image timestamps using manage.py randomize_timestamps command.
    To see all options and defaults of the manage.py randomize_timestamps command, use the --show-help option:
    uv run invoke randomize-timestamps --show-help
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py randomize_timestamps"
        f"{' --help' if show_help else ''} "
        f"{f' -c {character}' if character else ''}"
        f"{f' -n {n_days}' if n_days else ''}",
        pty=True,
    )


@task(
    help={
        "dry_run": "List files that would be removed without actually deleting them.",
        "media_root": "Override the media root directory (default: /app/media).",
    },
)
def clean_assets(c, dry_run=False, media_root=None):
    """
    Remove media files not referenced in the database using manage.py clean_assets command.
    """
    c.run(
        f"docker compose exec wagtail uv run manage.py clean_assets"
        f"{' --dry-run' if dry_run else ''}"
        f"{f' --media-root {media_root}' if media_root else ''}",
        pty=True,
    )
