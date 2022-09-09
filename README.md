# Checkmk Operator (WIP)

## Description

Checkmk is an Infrastructure and Application Monitoring tool. This operator is based on Checkmk Raw Edition (CRE) - it's Open Source and incorporates Nagios as its core.

## Usage

In order to deploy Checkmk Raw Edition, you can run:

```bash
$ juju deploy checkmk-k8s # --trust (use when cluster has RBAC enabled)
```

To monitor the deployment:
```bash
$ juju status
```

As soon as the status is active, you can get the IP address by status output in App.

You can access the GUI in Checkmk via `http://<address>:5000/cmk/check_mk/`.

To get the cmkadmin password, you can run the action get-admin-password:
```bash
$ juju run-action checkmk-k8s-operator/0 get-cmkadmin-password --wait
```

The output will be displayed as the example:
```bash
unit-checkmk-k8s-operator-0:
  UnitId: checkmk-k8s-operator/0
  id: "10"
  results:
    cmkadmin-password: 29dd4f91effe2084dd704322b134e69d
  status: completed
  timing:
    completed: 2022-08-31 20:57:01 +0000 UTC
    enqueued: 2022-08-31 20:56:59 +0000 UTC
    started: 2022-08-31 20:57:01 +0000 UTC
```

The nexts steps can be followed as described in `Getting started with monitoring` in [Checkmk Documentation](https://docs.checkmk.com/latest/en/checkmk_getting_started.html).

## Relations

No relations required.

## OCI Images

This charm uses [check-mk-raw](https://hub.docker.com/r/checkmk/check-mk-raw/) image provided by [Checkmk](https://checkmk.com/) and runs on Ubuntu 20.04.

## Contributing

Please see the [Juju SDK docs](https://juju.is/docs/sdk) for guidelines on enhancements to this
charm following best practice guidelines, and
[CONTRIBUTING.md](https://github.com/amandahla/checkmk-k8s-operator/blob/main/CONTRIBUTING.md) for developer
guidance.
