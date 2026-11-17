from version import (
    APP_NAME,
    VERSION,
    VERSION_TUPLE,
    get_display_name,
    get_executable_name,
    get_version,
    get_version_tuple,
)


def test_version_helpers():
    assert get_version() == VERSION
    assert get_version_tuple() == VERSION_TUPLE
    assert get_display_name() == f"{APP_NAME} v{VERSION}"
    assert get_executable_name() == f"{APP_NAME}_v{VERSION}.exe"
