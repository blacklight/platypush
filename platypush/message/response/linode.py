import datetime
from typing import List

from linode_api4.objects.linode import Instance, Config, Disk, Backup, Image, Kernel, Type

from platypush.message import Mapping
from platypush.message.response import Response


class LinodeResponse(Response):
    pass


class LinodeConfigModel(Mapping):
    def __init__(self, config: Config):
        super().__init__()
        self.comments = config.comments
        self.created = config.created
        self.helpers = config.helpers.dict
        self.id = config.id
        self.initrd = config.initrd
        self.kernel = dict(LinodeKernelModel(config.kernel))
        self.label = config.label
        self.linode_id = config.linode_id
        self.memory_limit = config.memory_limit
        self.parent_id_name = config.parent_id_name
        self.root_device = config.root_device
        self.run_level = config.run_level
        self.updated = datetime.datetime.fromisoformat(config.updated)
        self.virt_mode = config.virt_mode


class LinodeKernelModel(Mapping):
    def __init__(self, kernel: Kernel):
        super().__init__()
        self.architecture = kernel.architecture
        self.created = kernel.created
        self.deprecated = kernel.deprecated
        self.description = kernel.description
        self.id = kernel.id
        self.kvm = kernel.kvm
        self.label = kernel.label
        self.version = kernel.version
        self.xen = kernel.xen


class LinodeBackupModel(Mapping):
    def __init__(self, backup: Backup):
        super().__init__()
        self.created = backup.created
        self.disks = {
            disk.label: {
                'label': disk.label,
                'size': disk.size,
                'filesystem': disk.filesystem,
            }
            for disk in backup.disks
        }

        self.duration = backup.duration
        self.finished = backup.finished
        self.id = backup.id
        self.label = backup.label
        self.linode_id = backup.linode_id
        self.message = backup.message
        self.parent_id_name = backup.parent_id_name
        self.country = backup.region.country
        self.status = backup.status
        self.type = backup.type
        self.updated = backup.updated


class LinodeDiskModel(Mapping):
    def __init__(self, disk: Disk):
        super().__init__()
        self.created = disk.created
        self.filesystem = disk.filesystem
        self.id = disk.id
        self.label = disk.label
        self.linode_id = disk.linode_id
        self.parent_id_name = disk.parent_id_name
        self.size = disk.size
        self.status = disk.status
        self.updated = disk.updated


class LinodeImageModel(Mapping):
    def __init__(self, image: Image):
        super().__init__()
        self.created = image.created
        self.created_by = image.created_by
        self.deprecated = image.deprecated
        self.description = image.description
        self.is_public = image.is_public
        self.label = image.label
        self.size = image.size
        self.status = image.status
        self.type = image.type
        self.vendor = image.vendor


class LinodeTypeModel(Mapping):
    # noinspection PyShadowingBuiltins
    def __init__(self, type: Type):
        super().__init__()
        self.disk = type.disk
        self.id = type.id
        self.label = type.label
        self.memory = type.memory
        self.network_out = type.network_out
        self.price = type.price.dict
        self.transfer = type.transfer
        self.type_class = type.type_class
        self.vcpus = type.vcpus


class LinodeInstanceModel(Mapping):
    def __init__(self, node: Instance):
        super().__init__()
        self.label = node.label
        self.status = node.status
        self.alerts = node.alerts.dict
        self.available_backups = [
            dict(LinodeBackupModel(backup))
            for backup in node.available_backups.automatic
        ],

        self.backups = {
            'enabled': node.backups.enabled,
            'schedule': node.backups.schedule.dict,
            'last_successful': datetime.datetime.fromisoformat(node.backups.last_successful),
        }

        self.configs = {config.label: dict(LinodeConfigModel(config)) for config in node.configs}
        self.disks = {disk.label: dict(LinodeDiskModel(disk)) for disk in node.disks}
        self.group = node.group
        self.hypervisor = node.hypervisor
        self.id = node.id
        self.image = LinodeImageModel(node.image)
        self.country = node.region.country
        self.specs = node.specs.dict
        self.tags = node.tags
        self.transfer = node.transfer.dict
        self.type = dict(LinodeTypeModel(node.type))
        self.updated = node.updated


class LinodeInstanceResponse(LinodeResponse):
    def __init__(self, instance: Instance, *args, **kwargs):
        super().__init__(*args, output={
            'instance': dict(LinodeInstanceModel(instance))
        }, **kwargs)


class LinodeInstancesResponse(LinodeResponse):
    def __init__(self,
                 instances: List[Instance],
                 *args, **kwargs):
        super().__init__(*args, output={
            'instances': {instance.label: dict(LinodeInstanceModel(instance)) for instance in instances},
        }, **kwargs)


# vim:sw=4:ts=4:et:
