"""Main module."""
import sys
import os, argparse, pathlib, re, shlex, json, time
import git# comes from gitpython
import frontmatter# comes from python-frontmatter

def print_and_system(cmd):
    print(cmd)
    os.system(cmd)

class notebook:
    def get(self, *args): return self.frontmatter.get(*args)
    def __getitem__(self, key): return self.frontmatter.__getitem__(key)
    def __setitem__(self, *args): return self.frontmatter.__setitem__(*args)
    def setdefault(self, key, value): self[key] = self.get(key, value)

class raw_notebook(notebook):
    def __init__(self, content):
        self.content = content
        self.frontmatter = frontmatter.loads(content)
    def dump(self, path): frontmatter.dump(self.frontmatter, path)

class ipynb_notebook(notebook):
    def __init__(self, content):
        self.content = content
        self.json = json.loads(content)
        self.frontmatter = frontmatter.loads("".join(self.json["cells"][0]["source"]))
    def dump(self, path):
        self.json["cells"][0]["source"] = re.split(
            r"(?<=\n)", frontmatter.dumps(self.frontmatter)
        )
        path.write_text(json.dumps(self.json))

def get_notebook(content, suffix):
    return ipynb_notebook(content) if suffix == ".ipynb" else raw_notebook(content)

def find_and_copy_snapshots(args, path):
    # https://stackoverflow.com/questions/28803626/get-all-revisions-for-a-specific-file-in-gitpython
    suffix = path.suffix
    commits = list(args.repo.iter_commits(paths=[path]))
    versions = dict()
    # with open(path, "r") as fd: versions['latest'] = get_notebook(fd.read(), suffix)
    auto_version = 0
    nbs = []
    for commit in reversed(commits): 
        content = (commit.tree / str(path)).data_stream.read().decode("utf-8")
        nb = get_notebook(content, suffix)
        nb["date"] = time.strftime("%Y-%m-%d", time.gmtime(commit.committed_date))
        nb.setdefault("author", commit.author.name)
        version = nb.get("version", "unversioned")
        if version == "auto": 
            version = f"0.1.{auto_version}"
            auto_version += 1
        versions[version] = nb
        nbs += [nb]
    if not args.keep_unversioned: versions.pop("unversioned", None) 
    index_content = f"""---
title: {path.name}
date: {nbs[-1]["date"]}
---

version|title|description
-|--|---"""
    snapshot_base = args.snapshots_dir / path.relative_to(args.quarto_project).with_suffix("")
    if path.stem == "index": snapshot_base = snapshot_base.parent
    snapshot_base.mkdir(parents=True, exist_ok=True)
    for version, nb in reversed(versions.items()):
        # stem = "index" if version == "latest" else f"{path.stem}_{version}"
        stem = f"{path.stem}_{version}"
        # rel_path = path.relative_to(args.quarto_project).with_suffix("")
        snapshot_path = snapshot_base / f"{stem}{suffix}"
        print(f"Generating {snapshot_path}...")
        modified_title = nb.get("title", path.stem)
        link = snapshot_path.with_suffix(".html").name
        def make_link(x): return f"[{x}]({link})" 
        index_content += "\n" + "|".join(map(make_link, [
            version, nb.get("title", path.stem), nb.get("description", "No description")
        ]))
        modified_title += f" ({version})"
        if path == args.quarto_project / f"index{suffix}": 
            modified_title = "SNAPSHOTS"
            nb["order"] = 10 + nb.get("order", 0)
        nb["title"] = modified_title
        nb.dump(snapshot_path)
    if path.stem != "index":
        index_path = snapshot_base / "index.qmd"
        print(f"Generating {index_path}...")
        index_path.write_text(index_content)

def generate(args):
    args.repo = git.Repo(args.git_root)
    args.quarto_project = pathlib.Path(args.quarto_project)
    args.snapshots_dir = args.quarto_project / args.snapshots_subdir
    paths = sum([
        list(args.quarto_project.rglob(f"*.*{ext}")) 
        for ext in ["md", "qmd", "ipynb"] 
    ], [])
    for path in paths:
        try:
            path.relative_to(args.snapshots_dir)
            continue
        except:
            pass
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