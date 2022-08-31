#!/usr/bin/env python3
# Copyright 2022 Amanda Katz
# See LICENSE file for licensing details.
#
# Learn more at: https://juju.is/docs/sdk

"""Charmed Operator for Checkmk; an Infrastructure and Application Monitoring."""

import logging

from ops.charm import ActionEvent, CharmBase
from ops.framework import StoredState
from ops.main import main
from charms.observability_libs.v0.kubernetes_service_patch import KubernetesServicePatch
from ops.pebble import ExecError, Layer
from ops.model import ActiveStatus
import secrets

logger = logging.getLogger(__name__)


class CheckmkK8SOperatorCharm(CharmBase):
    """Charmed Operator for Checkmk, an Infrastructure and Application Monitoring."""

    _stored = StoredState()

    def __init__(self, *args):
        super().__init__(*args)
        self._stored.set_default(cmkadmin_password="")
        self.framework.observe(self.on.checkmk_pebble_ready, self._on_checkmk_pebble_ready)
        self.framework.observe(self.on.get_admin_password_action, self._on_get_admin_password)

        self._service_patcher = KubernetesServicePatch(
            self, [(self.app.name, 6557, 6557), (self.app.name, 5000, 5000)]
        )

    def _on_checkmk_pebble_ready(self, event):
        """Define checkmk peeble layer

        Args:
            event ([type]): event
        """
        container = self.unit.get_container("checkmk")
        container.add_layer("checkmk", self._checkmk_layer, combine=True)
        container.replan()
        self.unit.status = ActiveStatus()

    def _on_get_admin_password(self, event: ActionEvent) -> None:
        """Returns the initial generated password for the admin user as an action response

        Args:
            event (ActionEvent): Get Admin Password event
        """
        if not self._stored.cmkadmin_password:
            self._stored.cmkadmin_password = self._generate_cmkadmin_password()
        event.set_results({"cmkadmin-password": self._stored.cmkadmin_password})

    @property
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

    def _generate_cmkadmin_password(self) -> str:
        """Generates new cmkadmin password by calling omd command in the container

        Returns:
            str: New cmkadmin password - teste
        """
        container = self.unit.get_container("checkmk")

        new_password = secrets.token_hex(16)

        htpasswd_command = container.exec(
            ["htpasswd", "-b", "-m", "etc/passwd", "cmkadmin", new_password],
            timeout=5 * 60,
            user="cmk",
            group="cmk",
        )

        try:
            htpasswd_command.wait()
        except ExecError as e:
            logger.error("unable to get cmkadmin password")
            logger.debug(e.stderr)

        return new_password


if __name__ == "__main__":
    main(CheckmkK8SOperatorCharm)
