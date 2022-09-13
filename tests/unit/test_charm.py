# Copyright 2022 Amanda Katz
# See LICENSE file for licensing details.
#
# Learn more about testing at: https://juju.is/docs/sdk/testing

import unittest
from unittest.mock import Mock, patch

from ops.model import ActiveStatus
from ops.testing import Harness

from charm import CheckmkCharm


class TestCharm(unittest.TestCase):
    @patch("charm.KubernetesServicePatch", lambda x, y: None)
    def setUp(self):
        self.harness = Harness(CheckmkCharm)
        self.addCleanup(self.harness.cleanup)
        self.harness.begin()

    def test_checkmk_pebble_ready(self):
        # Check the initial Pebble plan is empty as well cmkadmin_password
        initial_plan = self.harness.get_container_pebble_plan("checkmk")
        self.assertEqual(initial_plan.to_yaml(), "{}\n")
        self.assertEqual(self.harness.charm._stored.cmkadmin_password, "")

        container = self.harness.model.unit.get_container("checkmk")

        # Emit the PebbleReadyEvent
        self.harness.charm.on.checkmk_pebble_ready.emit(container)

        # Get the plan now we've run PebbleReady
        updated_plan = self.harness.get_container_pebble_plan("checkmk").to_dict()

        # Check we've got the plan we expected
        self.assertEqual(self.harness.charm._checkmk_layer.to_dict(), updated_plan)

        # Check the service was started
        service = self.harness.model.unit.get_container("checkmk").get_service("checkmk")
        self.assertTrue(service.is_running())

        # Ensure we set an ActiveStatus with no message
        self.assertEqual(self.harness.model.unit.status, ActiveStatus())

    @patch("charm.CheckmkCharm._generate_cmkadmin_password")
    def test_get_cmkadmin_password_action(self, generate):
        mock_event = Mock()

        # Password expected
        generate.return_value = "password"

        # Trigger the event handler
        self.harness.charm._on_get_cmkadmin_password(mock_event)

        # Ensure stored state was updated with a generated password
        self.assertEqual(self.harness.charm._stored.cmkadmin_password, "password")

        # Ensure is called once
        generate.assert_called_once()

        # Make sure we return the generated password
        mock_event.called_once_with({"cmkadmin-password": "password]"})

        # Call again and make sure we don't call the generate_cmkadmin_password again
        generate.reset_mock()
        self.harness.charm._on_get_cmkadmin_password(mock_event)
        generate.assert_not_called()
