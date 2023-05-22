"""Main module."""
import sys
import os, argparse, pathlib, re, shlex
import git# comes from gitpython
import frontmatter# comes from python-frontmatter

def print_and_system(cmd):
    print(cmd)
    os.system(cmd)

def find_and_copy_snapshots(args, path):
    # https://stackoverflow.com/questions/28803626/get-all-revisions-for-a-specific-file-in-gitpython
    commits = list(args.repo.iter_commits(paths=[path]))
    versions = dict()
    contents = [
        (commit.tree / str(path)).data_stream.read().decode("utf-8")
        for commit in reversed(commits)
    ]
    with open(path, "r") as fd: versions['latest'] = fd.read()
    for content in contents: 
        version = frontmatter.loads(content).get("version", "unversioned")
        versions[version] = content
    if not args.keep_unversioned: versions.pop("unversioned", None) 
    for version, content in versions.items():
        stem = "index" if version == "latest" else f"{path.stem}_{version}"
        rel_path = path.relative_to(args.quarto_project).with_suffix("")
        if path.stem == "index": rel_path = rel_path.parent
        snapshot_path = args.snapshots_dir / rel_path / f"{stem}.qmd"
        snapshot_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"Generating {snapshot_path}...")
        modified_content = frontmatter.loads(content)
        modified_title = modified_content.get("title", path.stem)
        if version != "latest": modified_title += f" ({version})"
        if path == args.quarto_project / "index.md": modified_title = "SNAPSHOTS"
        modified_content["title"] = modified_title
        modified_content["order"] = 10 + modified_content.get("order", 0)
        frontmatter.dump(modified_content, snapshot_path)

def generate(args):
    args.repo = git.Repo(args.git_root)
    args.quarto_project = pathlib.Path(args.quarto_project)
    args.snapshots_dir = args.quarto_project / args.snapshots_subdir
    for path in args.quarto_project.rglob("*.*md"):
        try:
            path.relative_to(args.snapshots_dir)
        except:
            find_and_copy_snapshots(args, path)

def get_parser():
    parser = argparse.ArgumentParser(
        prog = "main", # Somebody come up with a good name
        description = "Runs and renders experiments",
    )
    parser.add_argument('-j', '--initialize-julia', default=False, action='store_true')
    parser.add_argument('-c', '--commit', default=False, action='store_true')
    parser.add_argument('-m', '--commit-message', default="autocommit")
    parser.add_argument('-g', '--generate', default=False, action='store_true')
    parser.add_argument('-r', '--render', default=False, action='store_true')
    parser.add_argument('-p', '--publish', default=False, action='store_true')
    parser.add_argument('-w', '--hello-world', default=False, action='store_true')
    parser.add_argument('--git-root', default=".")
    parser.add_argument('-q', '--quarto-project', default="quarto")
    parser.add_argument('-s', '--snapshots-subdir', default="snapshots")
    parser.add_argument('-k', '--keep-unversioned', default=False, action='store_true')
    return parser


def handle_args(args):
    print(args)

    if args.initialize_julia:
        julia_cmd = "using Pkg; Pkg.instantiate();"
        print_and_system(f"julia --project=. -e {shlex.quote(julia_cmd)}")
    if args.commit:
        print_and_system("git add .")
        print_and_system("git status")
        print_and_system(f"git commit -m {shlex.quote(args.commit_message)}")
        print_and_system("git push")
    if args.generate: generate(args)
    if args.render: print_and_system("quarto render quarto")
    if args.publish: print_and_system("quarto publish gh-pages quarto --no-prompt --no-browser")
    if args.hello_world: print("Hello quarto!")
    return 0

def main(): return handle_args(get_parser().parse_args())