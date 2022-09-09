# Copyright 2021 Canonical Ltd.
# See LICENSE file for licensing details.
import logging
from pathlib import Path

import yaml
from pytest import fixture
from pytest_operator.plugin import OpsTest

logger = logging.getLogger(__name__)


@fixture(scope="module")
async def checkmk_charm(ops_test: OpsTest):
    """Checkmk charm used for integration testing."""
    charm = await ops_test.build_charm(".")
    return charm


@fixture(scope="module")
def checkmk_metadata(ops_test: OpsTest):
    return yaml.safe_load(Path("./metadata.yaml").read_text())


@fixture(scope="module")
def checkmk_oci_image(ops_test: OpsTest, checkmk_metadata):
    return checkmk_metadata["resources"]["checkmk-image"]["upstream-source"]
