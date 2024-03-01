import pytest

from salt.exceptions import CommandExecutionError

pytestmark = [
    pytest.mark.destructive_test,
    pytest.mark.skip_unless_on_windows,
    pytest.mark.slow_test,
    pytest.mark.windows_whitelisted,
]


@pytest.fixture(scope="module")
def chocolatey(states):
    yield states.chocolatey


@pytest.fixture(scope="module")
def chocolatey_mod(modules):
    yield modules.chocolatey


@pytest.fixture()
def clean(chocolatey_mod):
    chocolatey_mod.unbootstrap()
    try:
        chocolatey_version = chocolatey_mod.chocolatey_version(refresh=True)
    except CommandExecutionError:
        chocolatey_version = None
    assert chocolatey_version is None
    yield
    chocolatey_mod.unbootstrap()


@pytest.fixture()
def installed(chocolatey_mod):
    chocolatey_mod.bootstrap(force=True)
    try:
        chocolatey_version = chocolatey_mod.chocolatey_version(refresh=True)
    except CommandExecutionError:
        chocolatey_version = None
    assert chocolatey_version is not None
    yield
    chocolatey_mod.unbootstrap()


def test_bootstrapped(chocolatey, chocolatey_mod, clean):
    ret = chocolatey.bootstrapped(name="junk name")
    assert "Installed chocolatey" in ret.comment
    assert ret.result is True
    try:
        chocolatey_version = chocolatey_mod.chocolatey_version(refresh=True)
    except CommandExecutionError:
        chocolatey_version = None
    assert chocolatey_version is not None


def test_bootstrapped_test_true(chocolatey, clean):
    ret = chocolatey.bootstrapped(name="junk name", test=True)
    assert ret.result is None
    assert ret.comment == "The latest version of Chocolatey will be installed"


def test_bootstrapped_version(chocolatey, chocolatey_mod, clean):
    ret = chocolatey.bootstrapped(name="junk_name", version="1.4.0")
    assert ret.comment == "Installed chocolatey 1.4.0"
    assert ret.result is True
    try:
        chocolatey_version = chocolatey_mod.chocolatey_version(refresh=True)
    except CommandExecutionError:
        chocolatey_version = None
    assert chocolatey_version == "1.4.0"


def test_bootstrapped_version_test_true(chocolatey, chocolatey_mod, clean):
    ret = chocolatey.bootstrapped(name="junk_name", version="1.4.0", test=True)
    assert ret.comment == "Chocolatey 1.4.0 will be installed"


def test_unbootstrapped_installed(chocolatey, chocolatey_mod, installed):
    ret = chocolatey.unbootstrapped(name="junk_name")
    assert "Uninstalled chocolatey" in ret.comment
    assert ret.result is True
    try:
        chocolatey_version = chocolatey_mod.chocolatey_version(refresh=True)
    except CommandExecutionError:
        chocolatey_version = None
    assert chocolatey_version is None


def test_unbootstrapped_installed_test_true(chocolatey, chocolatey_mod, installed):
    ret = chocolatey.unbootstrapped(name="junk_name", test=True)
    assert "will be removed" in ret.comment
    assert ret.result is None


def test_unbootstrapped_clean(chocolatey, chocolatey_mod, clean):
    ret = chocolatey.unbootstrapped(name="junk_name")
    assert ret.comment == "Chocolatey not found on this system"
    assert ret.result is True
