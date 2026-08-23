"""
conftest.py
~~~~~~~~~~~
"""

import pytest

from wildfire.config import Config
from wildfire.corpus import Corpus


@pytest.fixture
def corpus(tmp_path):
    cfg = Config(wildfire_dir=tmp_path / "Wildfire")
    return Corpus(cfg)
