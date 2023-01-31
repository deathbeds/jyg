"""Automation for jyg."""
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import typing
from pathlib import Path

import doit.tools


class C:
    """Constants."""

    NAME = "jyg"
    NPM_NAME = f"@deathbeds/{NAME}"
    OLD_VERSION = "0.1.0"
    VERSION = "0.1.1"
    PACKAGE_JSON = "package.json"
    PYPROJECT_TOML = "pyproject.toml"
    PLATFORM = platform.system()
    PY_VERSION = "{}.{}".format(sys.version_info[0], sys.version_info[1])
    ROBOT_DRYRUN = "--dryrun"
    NYC = ["jlpm", "nyc", "report", "--offline"]
    PABOT_DEFAULTS = [
        "--artifactsinsubfolders",
        "--artifacts",
        "png,log,txt,svg,ipynb,json",
    ]


class P:
    """Paths."""

    DODO = Path(__file__)
    ROOT = DODO.parent
    BINDER = ROOT / ".binder"
    BINDER_ENV_YAML = BINDER / "environment.yml"
    README = ROOT / "README.md"
    LICENSE = ROOT / "LICENSE"
    DOCS = ROOT / "docs"
    CI = ROOT / ".github"
    SCHEMA = ROOT / "schema"
    YARNRC = ROOT / ".yarnrc"
    YARN_LOCK = ROOT / "yarn.lock"
    JS = ROOT / "js"
    EXT_JS_WEBPACK = ROOT / "webpack.config.js"
    PY_SRC = ROOT / "src/jyg"
    PY_D = PY_SRC / "_d"
    PY_D_ETC = PY_D / "etc"
    PYPROJECT_TOML = ROOT / C.PYPROJECT_TOML
    DOCS_STATIC = DOCS / "_static"
    DOCS_PY = [*DOCS.glob("*.py")]
    DOCS_DICTIONARY = DOCS / "dictionary.txt"
    EXAMPLES = ROOT / "examples"
    LITE_JSON = EXAMPLES / "jupyter-lite.json"
    LITE_CONFIG = EXAMPLES / "jupyter_lite_config.json"
    ALL_EXAMPLE_IPYNB = [*EXAMPLES.rglob("*.ipynb")]
    ALL_EXAMPLES = [*EXAMPLES.rglob("*.md"), *ALL_EXAMPLE_IPYNB]
    PAGES_LITE = ROOT / "pages-lite"
    PAGES_LITE_CONFIG = PAGES_LITE / "jupyter_lite_config.json"
    PAGES_LITE_JSON = PAGES_LITE / "jupyter-lite.json"
    ESLINTRC = ROOT / ".eslintrc.js"
    PACKAGE_JSON = ROOT / C.PACKAGE_JSON
    ALL_PACKAGE_JSONS = [PACKAGE_JSON]
    MSG_SCHEMA_JSON = PY_SRC / "schema/jyg-msg.v0.schema.json"
    BOARD_SCHEMA_JSON = SCHEMA / "boards.json"
    PROXY_SCHEMA_JSON = SCHEMA / "window-proxy.json"
    SCRIPTS = ROOT / "scripts"
    PY_SCRIPTS = [*SCRIPTS.glob("*.py")]
    SCRIPT_SCHEMA_TO_PY = SCRIPTS / "schema2typeddict.py"
    SCRIPT_POST_SCHEMA_TO_PY = SCRIPTS / "postschema2typeddict.py"
    ATEST = ROOT / "atest"
    ATEST_FIXTURES = ATEST / "fixtures"
    ROBOT_SUITES = ATEST / "suites"
    REQS = CI / "reqs"
    DEMO_ENV_YAML = BINDER / "environment.yml"
    TEST_ENV_YAML = REQS / "environment-test.yml"
    DOCS_ENV_YAML = REQS / "environment-docs.yml"
    BASE_ENV_YAML = REQS / "environment-base.yml"
    BUILD_ENV_YAML = REQS / "environment-build.yml"
    LINT_ENV_YAML = REQS / "environment-lint.yml"
    ROBOT_ENV_YAML = REQS / "environment-robot.yml"
    ENV_INHERIT = {
        BUILD_ENV_YAML: [BASE_ENV_YAML],
        DEMO_ENV_YAML: [
            BASE_ENV_YAML,
            BUILD_ENV_YAML,
            DOCS_ENV_YAML,
            LINT_ENV_YAML,
            ROBOT_ENV_YAML,
            TEST_ENV_YAML,
        ],
        DOCS_ENV_YAML: [BUILD_ENV_YAML, BASE_ENV_YAML],
        TEST_ENV_YAML: [BASE_ENV_YAML, BUILD_ENV_YAML, ROBOT_ENV_YAML],
        LINT_ENV_YAML: [BASE_ENV_YAML, BUILD_ENV_YAML, ROBOT_ENV_YAML],
    }


class E:
    """Environment."""

    IN_CI = bool(json.loads(os.environ.get("CI", "false").lower()))
    BUILDING_IN_CI = bool(json.loads(os.environ.get("BUILDING_IN_CI", "false").lower()))
    TESTING_IN_CI = bool(json.loads(os.environ.get("TESTING_IN_CI", "false").lower()))
    IN_RTD = bool(json.loads(os.environ.get("READTHEDOCS", "False").lower()))
    IN_BINDER = bool(json.loads(os.environ.get("IN_BINDER", "0")))
    LOCAL = not (IN_BINDER or IN_CI or IN_RTD)
    PYTEST_ARGS = json.loads(os.environ.get("PYTEST_ARGS", "[]"))
    ROBOT_RETRIES = json.loads(os.environ.get("ROBOT_RETRIES", "0"))
    ROBOT_ATTEMPT = json.loads(os.environ.get("ROBOT_ATTEMPT", "0"))
    ROBOT_ARGS = json.loads(os.environ.get("ROBOT_ARGS", "[]"))
    PABOT_ARGS = json.loads(os.environ.get("PABOT_ARGS", "[]"))
    WITH_JS_COV = bool(json.loads(os.environ.get("WITH_JS_COV", "0")))
    PABOT_PROCESSES = int(json.loads(os.environ.get("PABOT_PROCESSES", "4")))


class B:
    """Build."""

    ENV = P.ROOT / ".venv" if E.LOCAL else Path(sys.prefix)
    HISTORY = [ENV / "conda-meta/history"] if E.LOCAL else []
    NODE_MODULES = P.ROOT / "node_modules"
    YARN_INTEGRITY = NODE_MODULES / ".yarn-integrity"
    BUILD = P.ROOT / "build"
    DIST = P.ROOT / "dist"
    DOCS = BUILD / "docs"
    JS_META_TSBUILDINFO = BUILD / ".src.tsbuildinfo"
    DOCS_BUILDINFO = DOCS / ".buildinfo"
    LITE = BUILD / "lite"
    STATIC = P.PY_D / f"share/jupyter/labextensions/{C.NPM_NAME}"
    STATIC_PKG_JSON = STATIC / C.PACKAGE_JSON
    WHEEL = DIST / f"jyg-{C.VERSION}-py3-none-any.whl"
    SDIST = DIST / f"jyg-{C.VERSION}.tar.gz"
    LITE_SHASUMS = LITE / "SHA256SUMS"
    NPM_TARBALL = DIST / f"deathbeds-jyg-{C.VERSION}.tgz"
    DIST_HASH_DEPS = [NPM_TARBALL, WHEEL, SDIST]
    DIST_SHASUMS = DIST / "SHA256SUMS"
    ENV_PKG_JSON = ENV / f"share/jupyter/labextensions/{C.NPM_NAME}/{C.PACKAGE_JSON}"
    PIP_FROZEN = BUILD / "pip-freeze.txt"
    REPORTS = BUILD / "reports"
    ROBOCOV = BUILD / "__robocov__"
    REPORTS_COV_XML = REPORTS / "coverage-xml"
    PYTEST_HTML = REPORTS / "pytest.html"
    PYTEST_COV_XML = REPORTS_COV_XML / "pytest.coverage.xml"
    HTMLCOV_HTML = REPORTS / "htmlcov/index.html"
    PAGES_LITE = BUILD / "pages-lite"
    PAGES_LITE_SHASUMS = PAGES_LITE / "SHA256SUMS"
    EXAMPLE_HTML = BUILD / "examples"
    BOARD_SCHEMA_TS = P.JS / "_boards.ts"
    PROXY_SCHEMA_TS = P.JS / "_windowProxy.ts"
    MSG_SCHEMA_PY = P.PY_SRC / "schema/msg_v0.py"
    MSG_SCHEMA_TS = P.JS / "_msgV0.ts"
    COVERAGE = BUILD / "coverage"
    COVERAGE_PY = BUILD / ".coverage"
    COVERAGE_PYTEST = COVERAGE / "pytest/.coverage"
    COVERAGE_ROBOT = COVERAGE / "robot/.coverage"
    ROBOT = REPORTS / "robot"
    ROBOT_SCREENSHOTS = ROBOT / "screenshots"
    ROBOT_LOG_HTML = ROBOT / "log.html"
    REPORTS_NYC = REPORTS / "nyc"
    REPORTS_NYC_HTML = REPORTS_NYC / "index.html"
    REPORTS_NYC_LCOV = REPORTS_NYC / "lcov.info"
    MYPY_CACHE = BUILD / ".mypy_cache"
    SPELLING = BUILD / "spelling"


class L:
    """Lint."""

    ALL_DOCS_MD = [*P.DOCS.rglob("*.md")]
    ALL_PY_SRC = [*P.PY_SRC.rglob("*.py")]
    ALL_BLACK = [P.DODO, *ALL_PY_SRC, *P.DOCS_PY, *P.PY_SCRIPTS]
    ALL_SRC_CSS = [*(P.ROOT / "style").rglob("*.css")]
    ALL_STYLE_ASSETS = [*P.JS.glob("style/**/*")]
    ALL_CSS = [*P.DOCS_STATIC.rglob("*.css"), *ALL_SRC_CSS]
    ALL_JSON = [
        *P.ATEST_FIXTURES.rglob("*.jupyterlab-settings"),
        *P.JS.glob("*/js/**/*.json"),
        *P.PY_D_ETC.rglob("*.json"),
        *P.ROOT.glob(".json"),
        *P.SCHEMA.glob("*.json"),
        P.MSG_SCHEMA_JSON,
    ]
    ALL_MD = [
        *P.ROOT.glob("*.md"),
        *P.DOCS.rglob("*.md"),
        *P.CI.rglob("*.md"),
        *P.EXAMPLES.glob("*.md"),
    ]
    ALL_TS = [*P.JS.glob("**/*.ts")]
    ALL_YML = [*P.BINDER.glob("*.yml"), *P.CI.rglob("*.yml"), *P.ROOT.glob("*.yml")]
    ALL_JS = [*P.ROOT.glob("*.js")]
    ALL_PRETTIER = [*ALL_JSON, *ALL_MD, *ALL_YML, *ALL_TS, *ALL_JS, *ALL_CSS]
    ALL_ROBOT = [*P.ATEST.rglob("*.robot"), *P.ATEST.rglob("*.resource")]


class U:
    """Utilities."""

    def do(args, **kwargs):
        """Run commands in an opinonated way."""
        cwd = kwargs.pop("cwd", P.ROOT)
        shell = kwargs.pop("shell", False)
        return doit.tools.CmdAction(args, shell=shell, cwd=cwd, **kwargs)

    def source_date_epoch():
        """Fetch the git commit date for reproducible builds."""
        return (
            subprocess.check_output(["git", "log", "-1", "--format=%ct"])
            .decode("utf-8")
            .strip()
        )

    def hash_files(hashfile, *hash_deps):
        """Generate a SHA256SUMS file."""
        from hashlib import sha256

        if hashfile.exists():
            hashfile.unlink()

        lines = [
            f"{sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(hash_deps)
        ]

        output = "\n".join(lines)
        print(output)
        hashfile.write_text(output)

    def pip_list():
        """Get the list of pip modules."""
        B.PIP_FROZEN.write_bytes(
            subprocess.check_output([sys.executable, "-m", "pip", "freeze"])
        )

    def copy_one(src, dest):
        """Copy a single file."""
        if not src.exists():
            raise ValueError(f"{src} does not exist")
        if not dest.parent.exists():
            dest.parent.mkdir(parents=True)
        if dest.exists():
            dest.unlink()
        shutil.copy2(src, dest)

    def copy_some(dest, srcs):
        """Copy a bunch of tiles file."""
        for src in srcs:
            U.copy_one(src, dest / src.name)

    def clean_some(*paths):
        """Clean some files or directories."""
        for path in paths:
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()

    def ensure_version(path: Path):
        """Verify versions are consistent."""
        text = path.read_text(encoding="utf-8")
        if path.name == C.PACKAGE_JSON:
            old = f'"version": "{C.OLD_VERSION}"'
            expected = f'"version": "{C.VERSION}"'
            parse = json.loads
        elif path.name == C.PYPROJECT_TOML:
            old = f'version = "{C.OLD_VERSION}"'
            expected = f'version = "{C.VERSION}"'
            parse = __import__("tomli").loads

        if expected in text:
            return True

        if E.IN_CI:
            print(f"{path} does not contain: {expected}")
            return False

        new_text = text.replace(old, expected)

        parse(new_text)

        print(f"Patching {path} with: {expected}")
        path.write_text(new_text)

    def update_env_fragments(dest_env: Path, src_envs: typing.List[Path]):
        """Normalize environments by magic comments."""
        dest_text = dest_env.read_text(encoding="utf-8")
        print(f"... adding packages to {dest_env.relative_to(P.ROOT)}")
        for src_env in src_envs:
            print(f"    ... from {src_env.relative_to(P.ROOT)}")
            src_text = src_env.read_text(encoding="utf-8")
            pattern = f"""  ### {src_env.name} ###"""
            src_chunk = src_text.split(pattern)[1]
            dest_chunks = dest_text.split(pattern)
            dest_text = "\n".join(
                [
                    dest_chunks[0].strip(),
                    pattern,
                    f"  {src_chunk.strip()}",
                    pattern,
                    f"  {dest_chunks[2].strip()}",
                ]
            )
        dest_env.write_text(dest_text.strip() + "\n")

    def rel(*paths):
        """Get paths relative to the root of the repo."""
        return [p.relative_to(P.ROOT) for p in paths]

    def rewrite_links(path: Path):
        """Tidy up links for protable documents."""
        text = path.read_text(encoding="utf-8")
        text = text.replace(".md", ".html")
        text = text.replace(".ipynb", ".ipynb.html")
        path.write_text(text)

    def normalize_json(path: Path):
        """Sort JSON."""
        old_text = path.read_text(encoding="utf-8")
        data = json.loads(old_text)
        new_text = json.dumps(data, indent=2, sort_keys=True)
        path.write_text(new_text, encoding="utf-8")
        subprocess.call(["jlpm", "prettier", "--write", "--list-different", path])

    def make_robot_tasks(extra_args=None):
        """Generate some tasks for robot framework."""
        extra_args = extra_args or []
        name = "robot"
        is_dryrun = C.ROBOT_DRYRUN in extra_args
        file_dep = [*B.HISTORY, *L.ALL_ROBOT]
        if is_dryrun:
            name = f"{name}:dryrun"
        else:
            file_dep += [B.PIP_FROZEN, *L.ALL_PY_SRC, *L.ALL_TS, *L.ALL_JSON]
        out_dir = B.ROBOT / U.get_robot_stem(attempt=1, extra_args=extra_args)
        targets = [
            out_dir / "output.xml",
            out_dir / "log.html",
            out_dir / "report.html",
        ]
        if not is_dryrun:
            targets += [out_dir / ".coverage"]

        actions = []
        if E.WITH_JS_COV and not is_dryrun:
            targets += [B.REPORTS_NYC_LCOV]
            actions += [
                (U.clean_some, [B.ROBOCOV, B.REPORTS_NYC]),
                (doit.tools.create_folder, [B.ROBOCOV]),
            ]
        yield dict(
            name=name,
            uptodate=[
                doit.tools.config_changed(dict(cov=E.WITH_JS_COV, args=E.ROBOT_ARGS))
            ],
            file_dep=file_dep,
            actions=[*actions, (U.run_robot_with_retries, [extra_args])],
            targets=targets,
        )

    def run_robot_with_retries(extra_args=None):
        """Try to run robot, a couple times."""
        fail_count = -1
        extra_args = [*(extra_args or []), *E.ROBOT_ARGS]
        is_dryrun = C.ROBOT_DRYRUN in extra_args
        attempt = 0 if is_dryrun else E.ROBOT_ATTEMPT
        retries = 0 if is_dryrun else E.ROBOT_RETRIES

        while fail_count != 0 and attempt <= retries:
            attempt += 1
            print("attempt {} of {}...".format(attempt, retries + 1), flush=True)
            start_time = time.time()
            fail_count = U.run_robot(attempt=attempt, extra_args=extra_args)
            print(
                fail_count,
                "failed in",
                int(time.time() - start_time),
                "seconds",
                flush=True,
            )

        if is_dryrun:
            return fail_count == 0

        final = B.ROBOT / "output.xml"

        all_robot = [
            str(p)
            for p in B.ROBOT.rglob("output.xml")
            if p != final and "dry_run" not in str(p) and "pabot_results" not in str(p)
        ]

        subprocess.call(
            [
                "python",
                "-m",
                "robot.rebot",
                "--name",
                "📺",
                "--nostatusrc",
                "--merge",
                *all_robot,
            ],
            cwd=B.ROBOT,
        )

        if not is_dryrun:
            subprocess.call(
                [
                    "coverage",
                    "combine",
                    "--keep",
                    f"--data-file={B.COVERAGE_ROBOT}",
                    *B.ROBOT.rglob(".*.coverage"),
                ]
            )

        if B.ROBOT_SCREENSHOTS.exists():
            shutil.rmtree(B.ROBOT_SCREENSHOTS)

        B.ROBOT_SCREENSHOTS.mkdir()

        for screen_root in B.ROBOT.glob("*/screenshots/*"):
            shutil.copytree(screen_root, B.ROBOT_SCREENSHOTS / screen_root.name)

        return fail_count == 0

    def get_robot_stem(attempt=0, extra_args=None, browser="firefox"):
        """Get the directory in B.ROBOT for this platform/app."""
        extra_args = extra_args or []

        browser = browser.replace("headless", "")

        stem = f"{C.PLATFORM[:3].lower()}_{C.PY_VERSION}_{browser}_{attempt}"

        if C.ROBOT_DRYRUN in extra_args:
            stem = "dry_run"

        return stem

    def run_robot(attempt=0, extra_args=None):
        """Actuall run robot framework once."""
        import lxml.etree as ET

        extra_args = extra_args or []

        stem = U.get_robot_stem(attempt=attempt, extra_args=extra_args)
        out_dir = B.ROBOT / stem

        if attempt > 1:
            extra_args += ["--loglevel", "TRACE"]
            prev_stem = U.get_robot_stem(attempt=attempt - 1, extra_args=extra_args)
            previous = B.ROBOT / prev_stem / "output.xml"
            if previous.exists():
                extra_args += ["--rerunfailed", str(previous)]

        runner = [
            "pabot",
            *("--processes", E.PABOT_PROCESSES),
            *C.PABOT_DEFAULTS,
            *E.PABOT_ARGS,
        ]

        if C.ROBOT_DRYRUN in extra_args:
            runner = ["robot"]

        args = [
            *runner,
            *(["--name", f"{C.PLATFORM[:3]}{C.PY_VERSION}"]),
            *(["--randomize", "all"]),
            # variables
            *(["--variable", f"ATTEMPT:{attempt}"]),
            *(["--variable", f"OS:{C.PLATFORM}"]),
            *(["--variable", f"PY:{C.PY_VERSION}"]),
            *(["--variable", f"ROBOCOV:{B.ROBOCOV}"]),
            *(["--variable", f"FIXTURES:{P.ATEST_FIXTURES}"]),
            # files
            *(["--xunit", out_dir / "xunit.xml"]),
            *(["--outputdir", out_dir]),
            # dynamic
            *extra_args,
        ]

        if out_dir.exists():
            print(">>> trying to clean out {}".format(out_dir), flush=True)
            try:
                shutil.rmtree(out_dir)
            except Exception as err:
                print(
                    "... error, hopefully harmless: {}".format(err),
                    flush=True,
                )

        if not out_dir.exists():
            print(
                ">>> trying to prepare output directory: {}".format(out_dir), flush=True
            )
            try:
                out_dir.mkdir(parents=True)
            except Exception as err:
                print(
                    "... Error, hopefully harmless: {}".format(err),
                    flush=True,
                )

        str_args = [
            *map(
                str,
                [
                    *args,
                    P.ROBOT_SUITES,
                ],
            )
        ]
        print(">>> ", " ".join(str_args), flush=True)

        proc = subprocess.Popen(str_args, cwd=P.ATEST)

        try:
            proc.wait()
        except KeyboardInterrupt:
            proc.kill()
            proc.wait()

        out_xml = out_dir / "output.xml"
        fail_count = -1

        try:
            root = ET.fromstring(out_xml.read_bytes())
            stat = root.xpath("//total/stat")
            fail_count = int(stat[0].attrib["fail"])
        except Exception as err:
            print(err)

        if fail_count != 0:
            for out_console in sorted(out_dir.rglob("robot_*.out")):
                print(out_console.relative_to(out_dir))
                print(out_console.read_text(encoding="utf-8"))

        return fail_count

    def check_one_spell(html: Path, findings: Path):
        """Check a single document for misspelled words."""
        proc = subprocess.Popen(
            [
                "hunspell",
                "-d=en-GB,en_US",
                "-p",
                P.DOCS_DICTIONARY,
                "-l",
                "-L",
                "-H",
                str(html),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate()
        out_text = "\n".join([stdout.decode("utf-8"), stderr.decode("utf-8")]).strip()
        out_text = "\n".join(sorted(set(out_text.splitlines())))
        findings.write_text(out_text, encoding="utf-8")
        if out_text.strip():
            print("...", html)
            print(out_text)
            return False


def task_setup():
    """Run setup commands."""
    if E.TESTING_IN_CI:
        return

    dedupe = []
    if E.LOCAL:
        dedupe = [["jlpm", "yarn-deduplicate", "-s", "fewer", "--fail"]]
        yield dict(
            name="conda",
            file_dep=[P.BINDER_ENV_YAML],
            targets=[*B.HISTORY],
            actions=[
                [
                    "mamba",
                    "env",
                    "update",
                    "--prefix",
                    B.ENV,
                    "--file",
                    P.BINDER_ENV_YAML,
                ]
            ],
        )

    if E.LOCAL or not B.YARN_INTEGRITY.exists():
        yield dict(
            name="yarn",
            file_dep=[
                P.YARNRC,
                P.PACKAGE_JSON,
                *B.HISTORY,
                *([P.YARN_LOCK] if P.YARN_LOCK.exists() else []),
            ],
            actions=[
                ["jlpm", *([] if E.LOCAL else ["--frozen-lockfile"])],
                *dedupe,
            ],
            targets=[B.YARN_INTEGRITY],
        )


def task_env():
    """Keep environment descriptions up-to-date."""
    for env_dest, env_src in P.ENV_INHERIT.items():
        yield dict(
            name=f"conda:{env_dest.name}",
            targets=[env_dest],
            file_dep=[*env_src],
            actions=[(U.update_env_fragments, [env_dest, env_src])],
        )


def task_watch():
    """Watch files and rebuild."""
    yield dict(
        name="js",
        actions=[["jlpm", "watch"]],
        file_dep=[B.YARN_INTEGRITY],
    )


def task_docs():
    """Build the docs."""
    yield dict(
        name="sphinx",
        file_dep=[*P.DOCS_PY, *L.ALL_MD, *B.HISTORY, B.WHEEL, B.LITE_SHASUMS],
        actions=[["sphinx-build", "-b", "html", "docs", "build/docs"]],
        targets=[B.DOCS_BUILDINFO],
    )


def task_dist():
    """Build distributions."""
    if E.TESTING_IN_CI:
        return

    def build_with_sde():
        import subprocess

        rc = subprocess.call(
            [
                "flit",
                "--debug",
                "build",
                "--setup-py",
                "--format=wheel",
                "--format=sdist",
            ],
            env=dict(**os.environ, SOURCE_DATE_EPOCH=U.source_date_epoch()),
        )
        return rc == 0

    yield dict(
        name="flit",
        file_dep=[*L.ALL_PY_SRC, P.PYPROJECT_TOML, B.STATIC_PKG_JSON],
        actions=[build_with_sde],
        targets=[B.WHEEL, B.SDIST],
    )

    yield dict(
        name="npm",
        file_dep=[
            B.JS_META_TSBUILDINFO,
            P.PACKAGE_JSON,
            P.LICENSE,
            P.README,
        ],
        targets=[B.NPM_TARBALL],
        actions=[
            (doit.tools.create_folder, [B.DIST]),
            U.do(["npm", "pack", P.ROOT], cwd=B.DIST),
        ],
    )

    yield dict(
        name="hash",
        file_dep=[*B.DIST_HASH_DEPS],
        targets=[B.DIST_SHASUMS],
        actions=[(U.hash_files, [B.DIST_SHASUMS, *B.DIST_HASH_DEPS])],
    )


def task_dev():
    """Prepare for interactive development."""
    if E.TESTING_IN_CI:
        ci_artifact = B.WHEEL if sys.version_info < (3, 8) else B.SDIST
        pip_args = [ci_artifact]
        py_dep = [ci_artifact]
    else:
        py_dep = [B.ENV_PKG_JSON]
        pip_args = [
            "-e",
            ".",
            "--ignore-installed",
            "--no-deps",
        ]
        yield dict(
            name="ext:lab",
            actions=[
                ["jupyter", "labextension", "develop", "--overwrite", "."],
            ],
            file_dep=[B.STATIC_PKG_JSON],
            targets=[B.ENV_PKG_JSON],
        )
        yield dict(
            name="ext:server",
            actions=[
                ["jupyter", "server", "extension", "enable", "--sys-prefix", C.NAME],
                ["jupyter", "server", "extension", "list"],
            ],
            file_dep=[B.ENV_PKG_JSON],
        )

    check = []

    if not E.IN_RTD:
        # avoid sphinx-rtd-theme
        check = [[sys.executable, "-m", "pip", "check"]]

    yield dict(
        name="py",
        file_dep=py_dep,
        targets=[B.PIP_FROZEN],
        actions=[
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-vv",
                *pip_args,
                "--no-build-isolation",
            ],
            *check,
            (doit.tools.create_folder, [B.BUILD]),
            U.pip_list,
        ],
    )


def task_test():
    """Run tests."""
    file_dep = [B.STATIC_PKG_JSON, *L.ALL_PY_SRC]

    if E.TESTING_IN_CI:
        file_dep = []

    yield dict(
        name="pytest",
        file_dep=[B.PIP_FROZEN, *file_dep],
        actions=[
            (U.clean_some, [B.COVERAGE_PYTEST]),
            [
                "coverage",
                "run",
                "--context=pytest",
                "--append",
                f"--data-file={B.COVERAGE_PYTEST}",
                "--branch",
                f"--source={P.PY_SRC.name}",
                "-m",
                "pytest",
                "-vv",
                "--ff",
                "--pyargs",
                P.PY_SRC.name,
                f"--html={B.PYTEST_HTML}",
                "--self-contained-html",
                "--hypothesis-show-statistics",
                "--color=yes",
                "--script-launch-mode=subprocess",
                "--tb=long",
                *E.PYTEST_ARGS,
            ],
        ],
        targets=[B.PYTEST_HTML, B.COVERAGE_PYTEST],
    )

    yield from U.make_robot_tasks()


def task_coverage():
    """Generate coverage reports."""
    yield dict(
        name="py:combine",
        file_dep=[B.COVERAGE_PYTEST],
        targets=[B.COVERAGE_PY],
        actions=[
            [
                "coverage",
                "combine",
                "--keep",
                f"--data-file={B.COVERAGE_PY}",
                B.COVERAGE_PYTEST,
                B.COVERAGE_ROBOT,
            ]
        ],
    )

    yield dict(
        name="py:html",
        file_dep=[B.COVERAGE_PY],
        targets=[B.HTMLCOV_HTML],
        actions=[
            [
                "coverage",
                "html",
                "--show-contexts",
                "--skip-empty",
                f"--data-file={B.COVERAGE_PY}",
                f"--directory={B.HTMLCOV_HTML.parent}",
            ]
        ],
    )

    yield dict(
        name="js:nyc",
        actions=[
            [
                *C.NYC,
                f"--temp-dir={B.ROBOCOV}",
                f"--report-dir={B.REPORTS_NYC}",
            ]
        ],
        targets=[B.REPORTS_NYC_HTML],
    )


def task_lint():
    """Essure/check source formatting."""
    version_uptodate = doit.tools.config_changed({"version": C.VERSION})

    pre_pretty_tasks = []

    for pkg_json in P.ALL_PACKAGE_JSONS:
        path = pkg_json.parent.relative_to(P.ROOT)
        name = f"js:{C.PACKAGE_JSON}:{path}"
        pre_pretty_tasks += [f"lint:{name}"]
        yield dict(
            uptodate=[version_uptodate],
            name=f"js:version:{path}",
            file_dep=[pkg_json],
            actions=[(U.ensure_version, [pkg_json])],
        )
        yield dict(
            name=name,
            task_dep=[f"lint:js:version:{path}"],
            file_dep=[pkg_json, B.YARN_INTEGRITY],
            actions=[
                (U.normalize_json, [pkg_json]),
                ["jlpm", "prettier-package-json", "--write", *U.rel(pkg_json)],
            ],
        )

    yield dict(
        name="js:prettier",
        file_dep=[*L.ALL_PRETTIER, B.YARN_INTEGRITY],
        task_dep=pre_pretty_tasks,
        actions=[
            [
                "jlpm",
                "prettier",
                "--write",
                "--list-different",
                *U.rel(*L.ALL_PRETTIER),
            ],
        ],
    )

    yield dict(
        name="js:eslint",
        task_dep=["lint:js:prettier"],
        file_dep=[*L.ALL_TS, P.ESLINTRC, B.YARN_INTEGRITY],
        actions=[
            [
                "jlpm",
                "eslint",
                "--cache",
                "--cache-location",
                *U.rel(B.BUILD / ".eslintcache"),
                "--config",
                *U.rel(P.ESLINTRC),
                "--ext",
                ".js,.jsx,.ts,.tsx",
                *([] if E.IN_CI else ["--fix"]),
                *U.rel(P.JS),
            ]
        ],
    )

    yield dict(
        name="version:py",
        uptodate=[version_uptodate],
        file_dep=[P.PYPROJECT_TOML],
        actions=[(U.ensure_version, [P.PYPROJECT_TOML])],
    )

    check = ["--check"] if E.IN_CI else []
    rel_black = U.rel(*L.ALL_BLACK)
    yield dict(
        name="py:black",
        file_dep=[*L.ALL_BLACK, *B.HISTORY, P.PYPROJECT_TOML],
        task_dep=["lint:version:py"],
        actions=[
            ["docformatter", *(check if E.IN_CI else ["--in-place"]), *rel_black],
            ["isort", "--quiet", *check, *rel_black],
            ["ssort", *check, *rel_black],
            ["black", "--quiet", *check, *rel_black],
        ],
    )

    for post_black in ["pyflakes", "pydocstyle"]:
        yield dict(
            name=f"py:{post_black}",
            file_dep=[*L.ALL_BLACK, *B.HISTORY, P.PYPROJECT_TOML],
            task_dep=["lint:py:black"],
            actions=[[post_black, *rel_black]],
        )

    yield dict(
        name="py:mypy",
        file_dep=[*L.ALL_BLACK, *B.HISTORY, P.PYPROJECT_TOML],
        task_dep=["lint:py:black"],
        actions=[["mypy", *L.ALL_PY_SRC]],
    )

    yield dict(
        name="py:project",
        file_dep=[P.PYPROJECT_TOML],
        actions=[["pyproject-fmt", P.PYPROJECT_TOML]],
    )

    yield dict(
        name="robot:tidy",
        file_dep=[*L.ALL_ROBOT, *B.HISTORY],
        actions=[["robotidy", *U.rel(P.ATEST)]],
    )

    yield dict(
        name="robot:cop",
        task_dep=["lint:robot:tidy"],
        file_dep=[*L.ALL_ROBOT, *B.HISTORY],
        actions=[["robocop", *U.rel(P.ATEST)]],
    )

    yield from U.make_robot_tasks(extra_args=[C.ROBOT_DRYRUN])


def task_build():
    """Build intermediate files."""
    if not (E.IN_CI or E.IN_BINDER or E.IN_RTD):
        yield dict(
            name="schema:json:ts",
            actions=[["jlpm", "build:schema"]],
            file_dep=[
                P.MSG_SCHEMA_JSON,
                P.BOARD_SCHEMA_JSON,
                P.PROXY_SCHEMA_JSON,
                B.YARN_INTEGRITY,
            ],
            targets=[B.MSG_SCHEMA_TS, B.BOARD_SCHEMA_TS, B.PROXY_SCHEMA_TS],
        )

        yield dict(
            name="schema:json:py",
            actions=[
                [
                    "python",
                    P.SCRIPT_SCHEMA_TO_PY,
                    f"--python={B.MSG_SCHEMA_PY}",
                    f"--json-schema={P.MSG_SCHEMA_JSON}",
                ],
                ["docformatter", "-i", B.MSG_SCHEMA_PY],
                ["black", "--quiet", B.MSG_SCHEMA_PY],
                [
                    "python",
                    P.SCRIPT_POST_SCHEMA_TO_PY,
                    B.MSG_SCHEMA_PY,
                    "Types for jyge messages.",
                ],
                ["ssort", B.MSG_SCHEMA_PY],
                ["isort", "--quiet", B.MSG_SCHEMA_PY],
                ["black", "--quiet", B.MSG_SCHEMA_PY],
            ],
            file_dep=[
                P.MSG_SCHEMA_JSON,
                B.YARN_INTEGRITY,
                P.SCRIPT_POST_SCHEMA_TO_PY,
                P.SCRIPT_SCHEMA_TO_PY,
                P.PYPROJECT_TOML,
            ],
            targets=[B.MSG_SCHEMA_PY],
        )

    uptodate = [doit.tools.config_changed(dict(WITH_JS_COV=E.WITH_JS_COV))]

    ext_dep = [
        P.PACKAGE_JSON,
        P.EXT_JS_WEBPACK,
        B.YARN_INTEGRITY,
        *L.ALL_CSS,
        *L.ALL_STYLE_ASSETS,
    ]

    if E.WITH_JS_COV:
        ext_task = "build:ext:cov"
    else:
        ext_task = "build:ext"
        ext_dep += [B.JS_META_TSBUILDINFO]
        yield dict(
            uptodate=uptodate,
            name="js",
            actions=[["jlpm", "build:lib"]],
            file_dep=[
                *L.ALL_TS,
                B.YARN_INTEGRITY,
                B.MSG_SCHEMA_TS,
                B.BOARD_SCHEMA_TS,
                B.PROXY_SCHEMA_TS,
            ],
            targets=[B.JS_META_TSBUILDINFO],
        )

    yield dict(
        uptodate=uptodate,
        name="ext",
        actions=[["jlpm", ext_task]],
        file_dep=ext_dep,
        targets=[B.STATIC_PKG_JSON],
    )


def task_lite():
    """Build the in-browser demo."""
    yield dict(
        name="build",
        file_dep=[
            P.LITE_CONFIG,
            P.LITE_JSON,
            B.ENV_PKG_JSON,
            *P.ALL_EXAMPLES,
            B.PIP_FROZEN,
        ],
        targets=[B.LITE_SHASUMS],
        actions=[
            U.do(
                ["jupyter", "lite", "--debug", "build"],
                cwd=P.EXAMPLES,
            ),
            U.do(
                ["jupyter", "lite", "doit", "--", "pre_archive:report:SHA256SUMS"],
                cwd=P.EXAMPLES,
            ),
        ],
    )


def task_site():
    """Build the static report website."""
    yield dict(
        name="build",
        file_dep=[
            B.ENV_PKG_JSON,
            B.HTMLCOV_HTML,
            B.PIP_FROZEN,
            B.REPORTS_NYC_HTML,
            B.ROBOT_LOG_HTML,
            P.PAGES_LITE_CONFIG,
            P.PAGES_LITE_JSON,
        ],
        targets=[B.PAGES_LITE_SHASUMS],
        actions=[
            U.do(
                ["jupyter", "lite", "--debug", "build"],
                cwd=P.PAGES_LITE,
            ),
            U.do(
                ["jupyter", "lite", "doit", "--", "pre_archive:report:SHA256SUMS"],
                cwd=P.PAGES_LITE,
            ),
        ],
    )


def task_serve():
    """Run webservers."""

    def lab():
        proc = subprocess.Popen(
            list(
                map(
                    str,
                    [
                        "jupyter",
                        "lab",
                        "--no-browser",
                        "--debug",
                        "--expose-app-in-browser",
                    ],
                )
            ),
            stdin=subprocess.PIPE,
        )

        try:
            proc.wait()
        except KeyboardInterrupt:
            print("attempting to stop lab, you may want to check your process monitor")
            proc.terminate()
            proc.communicate(b"y\n")
        finally:
            proc.wait()

        proc.wait()
        return True

    yield dict(
        name="lab",
        uptodate=[lambda: False],
        file_dep=[B.ENV_PKG_JSON, B.PIP_FROZEN],
        actions=[doit.tools.PythonInteractiveAction(lab)],
    )


@doit.create_after("docs")
def task_check():
    """Check the built documentation."""
    all_html = [
        p
        for p in sorted(B.DOCS.rglob("*.html"))
        if "_static" not in str(p.relative_to(B.DOCS))
    ]

    all_spell = [*all_html]

    for example in P.EXAMPLES.glob("*.ipynb"):
        out_html = B.EXAMPLE_HTML / f"{example.name}.html"
        all_spell += [out_html]
        yield dict(
            name=f"nbconvert:{example.name}",
            actions=[
                (doit.tools.create_folder, [B.EXAMPLE_HTML]),
                ["jupyter", "nbconvert", "--to=html", "--output", out_html, example],
                (U.rewrite_links, [out_html]),
            ],
            file_dep=[example],
            targets=[out_html],
        )

    yield dict(
        name="links",
        file_dep=[B.DOCS_BUILDINFO, *all_html],
        actions=[
            [
                "pytest-check-links",
                "-vv",
                "--check-anchors",
                "--check-links-ignore",
                "http.*",
                *all_html,
            ]
        ],
    )

    for html_path in all_spell:
        stem = html_path.relative_to(P.ROOT)
        report = B.SPELLING / f"{stem}.txt"
        yield dict(
            name=f"spelling:{stem}",
            actions=[
                (doit.tools.create_folder, [report.parent]),
                (U.check_one_spell, [html_path, report]),
            ],
            file_dep=[html_path, P.DOCS_DICTIONARY],
            targets=[report],
        )
