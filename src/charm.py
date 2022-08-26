#!/usr/bin/env python3
# Copyright 2022 Amanda Katz
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charmed Operator for Checkmk; an Infrastructure and Application Monitoring."""

import logging

from ops.charm import CharmBase
from ops.framework import StoredState
from ops.main import main
from charms.observability_libs.v0.kubernetes_service_patch import KubernetesServicePatch
from ops.pebble import Layer
from ops.model import ActiveStatus

logger = logging.getLogger(__name__)


class CheckmkK8SOperatorCharm(CharmBase):
    """Charmed Operator for Checkmk, an Infrastructure and Application Monitoring."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self.framework.observe(self.on.checkmk_pebble_ready, self._checkmk_pebble_ready)
        self.framework.observe(self.on.install, self._on_install)

        self._service_patcher = KubernetesServicePatch(
            self, [(self.app.name, 6557, 6557), (self.app.name, 5000, 5000)]
        )

    def _on_install(self, event):
        logger.info("Congratulations, the charm was properly installed!")

    def _checkmk_pebble_ready(self, event):
        """Define checkmk peeble layer

        Args:
            event ([type]): event
        """
        container = self.unit.get_container("checkmk")
        new_layer = self._checkmk_layer()
        container.add_layer("checkmk", new_layer, combine=True)
        container.replan()
        process = container.exec(["omd", "status"], timeout=5 * 60)
        _, warnings = process.wait_output()
        if warnings:
            for line in warnings.splitlines():
                logger.warning("OMD: %s", line.strip())

        self.unit.status = ActiveStatus()

    def _checkmk_layer(self) -> Layer:
        """Create the Pebble configuration layer for Checkmk.

        Returns:
            Layer: A `ops.checkmk.Layer` object with the current layer options
        """
        layer_config = {
            "summary": "Checkmk layer",
            "description": "Checkmk layer",
            "services": {
                "checkmk": {
                    "override": "replace",
                    "summary": "Checkmk service",
                    "command": "/docker-entrypoint.sh",
                    "startup": "enabled",
                    "environment": {
                        "CMK_LIVESTATUS_TCP": "on",
                    },
                }
            },
        }
        return Layer(layer_config)


if __name__ == "__main__":
    main(CheckmkK8SOperatorCharm)
