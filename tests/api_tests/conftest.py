"""api_tests 局部 conftest。"""
import pytest


def pytest_collection_modifyitems(items):
    """收集阶段自动给 api_tests 下的用例打上 api 标记，使 -m "api" 可筛选。"""
    for item in items:
        if "api_tests" in str(item.fspath):
            item.add_marker(pytest.mark.api)