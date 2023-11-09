#! /usr/bin/env python3
import argparse
import os
from pathlib import Path
import subprocess

from github import Auth, Github


def run(args):
    """Runs this test."""

    token = args.token
    if token is None:
        token = os.getenv("GITHUB_TOKEN")
        if token is None:
            # Get token from gh app.
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

    sha = args.sha
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
    parser.add_argument("-a", "--all",
        help = "Update all AppImages",
        action = 'store_true',
        default = False
    )
    parser.add_argument("-d", "--dry",
        help = "Perform a dry run",
        action = 'store_true',
        default = False
    )
    parser.add_argument("-t", "--token",
        help = "GitHub authentication token"
    )
    parser.add_argument("-s", "--sha",
        help = "Target commit SHA"
    )

    args = parser.parse_args()
    print(args)
    run(args)
