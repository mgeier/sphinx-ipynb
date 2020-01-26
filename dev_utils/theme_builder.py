import argparse
from pprint import pformat
import shutil
import sys
import os

try:
    import git
except ImportError as e:
    print(
        "'GitPython', which is needed to run this tool, isn't installed."
        "To install it, run\n:'pip install GitPython'"
    )
    raise e

from sphinx.cmd.build import build_main

REPO_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ROOT_DOC_DIR = os.path.join(REPO_ROOT_DIR, "doc")

DEV_UTILS_DIR = os.path.join(REPO_ROOT_DIR, "dev_utils")
TEMP_DIR = os.path.join(DEV_UTILS_DIR, "tmp")
TEMP_DOC_DIR = os.path.join(TEMP_DIR, "doc")
TEMP_BUILD_ROOT_DIR = os.path.join(DEV_UTILS_DIR, "_build")


def format_list(input_list):
    """
    Pretty formats list for printing.

    Parameters
    ----------
    input_list : List
        List to be printed.

    Returns
    -------
    str
        Pretty formated list.
    """
    return pformat(input_list, compact=True)


class InvalidThemeException(Exception):
    def __init__(self, invalid_themes, valid_themes):
        """
        Exception thrown when a theme name given via the cli isn't supported.

        Parameters
        ----------
        invalid_themes : List[str]
            List of invalid theme names.
        valid_themes : List[str]
            List of valid theme names.
        """
        super().__init__(
            "\nYou used the following invalid theme names:\n{}"
            "\nThe valid theme names are:\n{}".format(
                format_list(invalid_themes), format_list(["all"] + valid_themes)
            )
        )


class ThemeBuilder:
    """
    Class to interact with git and build the html docs
    for the different theme branches.
    """

    def __init__(self):
        self.prepare_git()
        self.theme_branche_refs = self.get_theme_branch_refs()
        self.build_args = []
        self.shared_cache_args = ["-d", os.path.join(TEMP_DIR, "shared_build_cache")]

    def prepare_git(self):
        """
        Creates a temporary git repository, which is used to extract
        the difference of theme branches to their base branch.
        """
        fetch_needed = False
        if os.path.isdir(os.path.join(TEMP_DIR, ".git")):
            self.repo = git.Repo(TEMP_DIR)
        else:
            self.repo = git.Repo.init(TEMP_DIR)
            fetch_needed = True

        remote_name = "upstream_diff_repo"

        if remote_name not in self.repo.remotes:
            self.remote = self.repo.create_remote(
                remote_name, "git@github.com:spatialaudio/nbsphinx.git"
            )
        else:
            self.remote = self.repo.remotes[remote_name]

        if fetch_needed:
            self.fetch_remote()
        self.repo.create_head("master", self.remote.refs.master)

    def fetch_remote(self):
        """
        Fetches the remote refs
        """
        self.remote.fetch()

    def get_theme_branch_refs(self):
        """
        Returns the list of theme branch references.

        Returns
        -------
        List[str]
            List of branch refs that end with '-theme'
        """
        theme_branche_refs = []
        for remote_brach in self.remote.refs:
            if remote_brach.name.endswith("-theme"):
                theme_branche_refs.append(remote_brach.name)
        return theme_branche_refs

    def get_diff_string(self, branch_ref, file_path):
        """
        Extracts the diff of the last commit for the file at file_path
        on the brach branch_ref.

        Parameters
        ----------
        branch_ref : str
            Brach reference of a theme branch which should be compared to its base.
        file_path : str
            Path of the file which diff should be extracted.

        Returns
        -------
        str
            Diff of the file on branch_ref and its base
        """
        theme_specific_commit, base_branch_commit = list(
            self.repo.iter_commits(branch_ref, max_count=2)
        )
        diff_index = base_branch_commit.diff(
            theme_specific_commit,
            paths=file_path,
            create_patch=True,
            unified=0,
        )
        for diff_item in diff_index.iter_change_type("M"):
            diff_lines = diff_item.diff.decode("utf-8").splitlines(keepends=True)
            added_lines = filter(lambda line: line.startswith("+"), diff_lines)
            return "".join([added_line.replace("+", "", 1) for added_line in added_lines])
        return ""

    def get_theme_requirements(self):
        """
        Reads all the diff of 'doc/requirements.txt' for all theme branches
        and writes them to 'dev_utils/theme_requirements.txt',
        so they can be installed all at once.
        """
        print(
            "Building new 'dev_utils/requirements_themes.txt'.\n"
            "Make sure that all requirements are installed by running:\n"
            "'pip install -r dev_utils/requirements_themes.txt' "
            "from the repo root."
        )
        theme_requirement_list = ["-r ../doc/requirements.txt\n"]
        for theme_branche_ref in self.theme_branche_refs:
            theme_requirement_list.append(
                self.get_diff_string(theme_branche_ref, "doc/requirements.txt")
            )
        requirement_file_path = os.path.join(DEV_UTILS_DIR, "requirements_themes.txt")
        with open(requirement_file_path, "w") as theme_requirements:
            theme_requirements.write("".join(theme_requirement_list))

    @staticmethod
    def copy_root_docs():
        """
        Copyes all needed files to build the docs from the repository root
        to the corresponding position in 'DEV_UTILS_DIR'.
        """
        shutil.rmtree(TEMP_DOC_DIR, ignore_errors=True)
        shutil.copytree(ROOT_DOC_DIR, TEMP_DOC_DIR)
        for file_name in ["README.rst", "CONTRIBUTING.rst"]:
            shutil.copyfile(
                os.path.join(REPO_ROOT_DIR, file_name),
                os.path.join(TEMP_DIR, file_name),
            )

    def update_theme_conf(self, branch_ref):
        """
        Appends the diff of the theme branch to its base brach,
        to the current 'doc/conf.py'

        Parameters
        ----------
        branch_ref : str
            Brach reference of a theme branch.
        """
        conf_diff = self.get_diff_string(branch_ref, "doc/conf.py")
        with open(os.path.join(ROOT_DOC_DIR, "conf.py")) as orig_conf_file:
            orig_conf = orig_conf_file.read()
        with open(os.path.join(TEMP_DOC_DIR, "conf.py"), "w") as temp_conf_file:
            temp_conf_file.write(orig_conf + conf_diff)

    def build_theme(self, branch_ref):
        """
        Build the html docs of the theme given by branch_ref.

        Parameters
        ----------
        branch_ref : str
            Brach reference of a theme branch.

        Raises
        ------
        Exception
            Exception raised when build_main exits with a none zero code.
            i.e. KeyboardInterrupt, so theme build don't need to be chanceled one by one.
        """
        branch_name = branch_ref.split("/")[1]
        print("\n\n")
        print("#" * 80)
        print("#", "BUILDING BRANCH: {}".format(branch_name.upper()).center(76), "#")
        print("#" * 80)
        self.update_theme_conf(branch_ref)
        dest_dir = os.path.join(TEMP_BUILD_ROOT_DIR, branch_name)
        build_args = [TEMP_DOC_DIR, dest_dir] + self.build_args
        # the theme "guzzle" and "press" need
        if self.ref_to_theme_name(branch_ref) not in ["guzzle", "press"]:
            build_args += self.shared_cache_args
        if build_main(build_args) != 0:
            raise Exception("An Error occurred building the docs.")

    def ref_to_theme_name(self, branch_ref):
        """
        Converts a branch_ref to the theme name.

        Parameters
        ----------
        branch_ref : str
            Brach reference of a theme branch.

        Returns
        -------
        str
            Theme name
        """
        return branch_ref.split("/")[1].replace("-theme", "", 1)

    def get_theme_names(self):
        """
        Return a list of all valid theme names.

        Returns
        -------
        List[str]
            Valid theme names.
        """
        theme_names = [
            self.ref_to_theme_name(theme_branch_ref)
            for theme_branch_ref in self.theme_branche_refs
        ]
        return theme_names

    def validate_theme_list(self, theme_list):
        """
        Validates theme_list and throws InvalidThemeException if 'all'
        isn't in the list and any theme name isn't valid.

        Parameters
        ----------
        theme_list : List[str]
            List of theme names.

        Raises
        ------
        InvalidThemeException
            If a theme name provided in theme_list isn't valid.
        """
        valid_themes = self.get_theme_names()
        invalid_themes = []
        if "all" in theme_list:
            return
        else:
            for theme_name in theme_list:
                if theme_name not in valid_themes:
                    invalid_themes.append(theme_name)
        if len(invalid_themes):
            raise InvalidThemeException(invalid_themes, valid_themes)

    def build_themes(self, theme_list):
        """
        Builds the themes with the name provided by themelist.

        Parameters
        ----------
        theme_list : List[str]
            List of theme names.
        """
        self.validate_theme_list(theme_list)
        self.copy_root_docs()
        for branch_ref in self.theme_branche_refs:
            if "all" in theme_list:
                self.build_theme(branch_ref)
            elif self.ref_to_theme_name(branch_ref) in theme_list:
                self.build_theme(branch_ref)


def cli(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(usage="python %(prog)s [OPTIONS]",)
    parser.add_argument(
        "-t",
        "--themes",
        default="all",
        dest="themes",
        nargs="*",
        help="List of theme names which should be build (default: 'all')",
    )
    parser.add_argument(
        "-a",
        action="store_true",
        dest="force_all",
        help="Write all files (default: only write new and changed files)",
    )
    parser.add_argument(
        "-l",
        action="store_true",
        dest="list_themes",
        help="Show all available themes and exit.",
    )
    parser.add_argument(
        "-r",
        action="store_true",
        dest="build_requirements",
        help="Build the requirements file to build all theme.",
    )
    parser.add_argument(
        "--fetch", action="store_true", dest="fetch", help="Fetch remote refs",
    )
    args = parser.parse_args(argv)
    theme_builder = ThemeBuilder()

    if args.fetch:
        theme_builder.fetch_remote()

    if args.list_themes:
        print(
            "The available themes are:\n{}".format(
                format_list(theme_builder.get_theme_names())
            )
        )
        return

    if (
        not os.path.isfile(os.path.join(DEV_UTILS_DIR, "requirements_themes.txt"))
        or args.build_requirements
    ):
        theme_builder.get_theme_requirements()
        return

    if args.force_all:
        theme_builder.build_args += ["-a"]

    theme_builder.build_themes(args.themes)


if __name__ == "__main__":
    cli()
