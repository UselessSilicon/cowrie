"""
dig command
"""

from __future__ import annotations

from cowrie.shell.command import HoneyPotCommand

commands = {}


class Command_git(HoneyPotCommand):
    APP_NAME = "git"

    def call(self):
        if not self.args:
            self.display_usage()
            return

        path = self.protocol.cwd
        subcommand = self.args[0]

        if subcommand == "--version":
            self.write("git version 2.34.1\n")

        elif subcommand == "clone":
            if len(self.args) < 2:
                self.write("fatal: You must specify a repository to clone.\n")
            else:
                repo = self.args[1].split("/")[-1].replace(".git", "")

                pname = self.fs.resolve_path(repo, path)
                if self.fs.exists(pname):
                    self.write(
                        f"fatal: destination path '{repo}' already exists and is not an empty directory."
                    )
                else:
                    self.fs.mkdir(
                        pname,
                        self.protocol.user.uid,
                        self.protocol.user.gid,
                        4096,
                        16877,
                    )

                    initialize_git = self.fs.resolve_path(".git", path + "/" + repo)
                    self.fs.mkdir(
                        initialize_git,
                        self.protocol.user.uid,
                        self.protocol.user.gid,
                        4096,
                        16877,
                    )

                    self.write(f"Cloning into '{repo}'...\n")
                    self.write("remote: Enumerating objects: 10, done.\n")
                    self.write("remote: Counting objects: 100% (10/10), done.\n")
                    self.write("remote: Compressing objects: 100% (8/8), done.\n")
                    self.write(
                        "remote: Total 10 (delta 13), reused 8 (delta 55), pack-reused 23 (from 1)\n"
                    )
                    self.write(
                        "Receiving objects: 100% (10/10), 1.23 MiB | 1.23 MiB/s, done.\n"
                    )
                    self.write("Resolving deltas: 100% (14/14), done.\n")
        elif subcommand == "init":
            pname = self.fs.resolve_path(".git", path)

            if self.fs.exists(pname):
                self.errorWrite(
                    f"Reinitialized existing Git repository in {path}/.git/\n"
                )
            else:
                self.fs.mkdir(
                    pname, self.protocol.user.uid, self.protocol.user.gid, 4096, 16877
                )
                self.write(f"Initialized empty Git repository in {path}/.git/\n")

        elif subcommand == "status":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("On branch master\n")
                self.write("Your branch is up to date with 'origin/master'.\n\n")
                self.write("nothing to commit, working tree clean\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "add":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                # Silently succeed (git add doesn't output anything on success)
                pass
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "commit":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                # Check for -m flag
                if len(self.args) > 1 and self.args[1] == "-m":
                    self.write("[master abc1234] ")
                    if len(self.args) > 2:
                        self.write(f"{self.args[2]}\n")
                    else:
                        self.write("commit message\n")
                    self.write(" 1 file changed, 1 insertion(+), 0 deletions(-)\n")
                else:
                    self.errorWrite(
                        "error: gpg failed to sign the data\nfatal: failed to write commit object\n"
                    )
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "push":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("Enumerating objects: 3, done.\n")
                self.write("Counting objects: 100% (3/3), done.\n")
                self.write("Writing objects: 100% (3/3), 256 bytes | 256.00 KiB/s, done.\n")
                self.write("Total 3 (delta 0), reused 0 (delta 0)\n")
                self.write("To origin\n")
                self.write("   abc1234..def5678  master -> master\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "pull":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("Already up to date.\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "log":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("commit abc1234567890def1234567890abcdef12345678\n")
                self.write("Author: User <user@example.com>\n")
                self.write("Date:   Mon Jan 1 12:00:00 2024 +0000\n\n")
                self.write("    Initial commit\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "branch":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("* master\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "checkout":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                if len(self.args) > 1:
                    branch = self.args[1]
                    self.write(f"Switched to branch '{branch}'\n")
                else:
                    self.errorWrite(
                        "error: pathspec '' did not match any file(s) known to git\n"
                    )
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "diff":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                # Empty output means no changes
                pass
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "remote":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                self.write("origin\n")
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand == "config":
            pname = self.fs.resolve_path(".git", path)
            if self.fs.exists(pname):
                # Most config commands don't output anything
                pass
            else:
                self.write(
                    "fatal: not a git repository (or any of the parent directories): .git\n"
                )

        elif subcommand in ("help", "--help", "-h"):
            self.display_usage()

        else:
            self.write(f"git: '{subcommand}' is not a git command. See 'git --help'.\n")

    def short_usage(self):
        self.write(
            "usage: git [-v | --version] [-h | --help] [-C <path>] [-c <name>=<value>]\n"
        )
        self.write(
            "           [--exec-path[=<path>]] [--html-path] [--man-path] [--info-path]\n"
        )
        self.write(
            "           [-p | --paginate | -P | --no-pager] [--no-replace-objects] [--bare]\n"
        )
        self.write(
            "           [--git-dir=<path>] [--work-tree=<path>] [--namespace=<name>]\n"
        )
        self.write(
            "           [--super-prefix=<path>] [--config-env=<name>=<envvar>]\n"
        )
        self.write("           <command> [<args>]\n\n")

    def display_usage(self):
        self.short_usage()
        self.write("These are common Git commands used in various situations:\n\n")

        self.write("start a working area (see also: git help tutorial)\n")
        self.write("   clone     Clone a repository into a new directory\n")
        self.write(
            "   init      Create an empty Git repository or reinitialize an existing one\n\n"
        )

        self.write("work on the current change (see also: git help everyday)\n")
        self.write("   add       Add file contents to the index\n")
        self.write("   mv        Move or rename a file, a directory, or a symlink\n")
        self.write("   restore   Restore working tree files\n")
        self.write(
            "   rm        Remove files from the working tree and from the index\n\n"
        )

        self.write("examine the history and state (see also: git help revisions)\n")
        self.write(
            "   bisect    Use binary search to find the commit that introduced a bug\n"
        )
        self.write(
            "   diff      Show changes between commits, commit and working tree, etc\n"
        )
        self.write("   grep      Print lines matching a pattern\n")
        self.write("   log       Show commit logs\n")
        self.write("   show      Show various types of objects\n")
        self.write("   status    Show the working tree status\n\n")

        self.write("grow, mark and tweak your common history\n")
        self.write("   branch    List, create, or delete branches\n")
        self.write("   commit    Record changes to the repository\n")
        self.write("   merge     Join two or more development histories together\n")
        self.write("   rebase    Reapply commits on top of another base tip\n")
        self.write("   reset     Reset current HEAD to the specified state\n")
        self.write("   switch    Switch branches\n")
        self.write(
            "   tag       Create, list, delete or verify a tag object signed with GPG\n\n"
        )

        self.write("collaborate (see also: git help workflows)\n")
        self.write("   fetch     Download objects and refs from another repository\n")
        self.write(
            "   pull      Fetch from and integrate with another repository or a local branch\n"
        )
        self.write("   push      Update remote refs along with associated objects\n\n")

        self.write(
            "'git help -a' and 'git help -g' list available subcommands and some\n"
        )
        self.write("concept guides. See 'git help <command>' or 'git help <concept>'\n")
        self.write("to read about a specific subcommand or concept.\n")
        self.write("See 'git help git' for an overview of the system.\n")


commands["/bin/git"] = Command_git
commands["git"] = Command_git
