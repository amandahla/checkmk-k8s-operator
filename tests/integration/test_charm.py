#!/usr/bin/env python3
# Copyright 2022 Canonical Ltd.
# See LICENSE file for licensing details.


import asyncio
import logging

import pytest
import requests
from pytest_operator.plugin import OpsTest
from tenacity import retry
from tenacity.stop import stop_after_attempt
from tenacity.wait import wait_exponential as wexp

logger = logging.getLogger(__name__)

APPNAME = "checkmk"


@pytest.mark.abort_on_fail
async def test_build_and_deploy(ops_test: OpsTest, checkmk_charm, checkmk_oci_image):
    """Builds charm using checkmk_charm and then deploy it.

    Args:
        ops_test (OpsTest): Operator test
        checkmk_charm (function): function that builds charm
        checkmk_oci_image (str): defined in field upstream-source in metadata.yaml
    """
    await asyncio.gather(
        ops_test.model.deploy(
            await checkmk_charm,
            application_name=APPNAME,
            resources={"checkmk-image": checkmk_oci_image},
            trust=True,
        ),
        ops_test.model.wait_for_idle(apps=[APPNAME], status="active", timeout=1000),
    )


@pytest.mark.abort_on_fail
@retry(wait=wexp(multiplier=2, min=1, max=30), stop=stop_after_attempt(10), reraise=True)
async def test_application_is_up(ops_test: OpsTest):
    """Tests if Checkmk is up.

    Args:
        ops_test (OpsTest): Operator test

    Returns:
        bool: check if status code is 200 (OK HTTP)
    """
    status = await ops_test.model.get_status()
    address = status["applications"][APPNAME]["public-address"]
    url = f"http://{address}:5000/cmk/check_mk/"
    logging.info(f"accessing {url}")
    response = requests.get(url)
    return response.status_code == 200
