#! /usr/bin/env python3
import argparse
from pathlib import Path
import subprocess

from github import Auth, Github


def run(token=None, sha=None):
    """Runs this test."""

    if token is None:
        # Get token from gh app (e.g. for local runs).
        p = subprocess.run(
            "gh auth token",
            shell = True,
            capture_output = True,
            check = True
        )
        token = p.stdout.decode().strip()

    auth = Auth.Token(token)
    repo = Github(auth=auth) \
        .get_repo("niess/test-releases")

    if sha is not None:
        ref = repo.get_git_ref("tags/rolling")
        if ref.ref is not None:
            ref.edit(
                sha = sha,
                force = True
            )

    for release in repo.get_releases():
        if release.tag_name == "rolling":
            break
    else:
        release = repo.create_git_release(
            tag = "rolling",
            name = "Rolling Release",
            message = "Testing a rolling release"
        )

    path = Path(__file__)
    for asset in release.assets:
        if asset.name == path.name:
            break
    else:
        asset = release.upload_asset(
            path = str(path),
            label = path.name
        )

    release.update_release(
        name = "Rolling Release",
        message = "Updated rolling release"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Test managing releases with GitHub API."
    )
    parser.add_argument("-t", "--token",
        help = "GitHub authentication token"
    )
    parser.add_argument("-s", "--sha",
        help = "Target commit SHA"
    )

    args = parser.parse_args()
    run(
        token = args.token,
        sha = args.sha
    )
