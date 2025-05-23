import os
import traceback
from typing import Optional, Dict, Any, List

import rclpy
from unilabos_msgs.msg import Resource  # type: ignore
from unilabos_msgs.srv import ResourceAdd  # type: ignore
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.timer import Timer

from unilabos.ros.initialize_device import initialize_device_from_dict
from unilabos.ros.msgs.message_converter import (
    convert_to_ros_msg,
)
from unilabos.ros.nodes.presets.host_node import HostNode
from unilabos.ros.x.rclpyx import run_event_loop_in_thread
from unilabos.utils import logger
from unilabos.config.config import BasicConfig


def exit() -> None:
    """关闭ROS节点和资源"""
    host_instance = HostNode.get_instance()
    if host_instance is not None:
        # 停止发现定时器
        # noinspection PyProtectedMember
        if hasattr(host_instance, "_discovery_timer") and isinstance(host_instance._discovery_timer, Timer):
            # noinspection PyProtectedMember
            host_instance._discovery_timer.cancel()
        for _, device_node in host_instance.devices_instances.items():
            if hasattr(device_node, "destroy_node"):
                device_node.ros_node_instance.destroy_node()
        host_instance.destroy_node()
    rclpy.shutdown()


def main(
    devices_config: Dict[str, Any] = {},
    resources_config={},
    graph: Optional[Dict[str, Any]] = None,
    controllers_config: Dict[str, Any] = {},
    bridges: List[Any] = [],
    args: List[str] = ["--log-level", "debug"],
    discovery_interval: float = 5.0,
) -> None:
    """主函数"""
    rclpy.init(args=args)
    rclpy.__executor = executor = MultiThreadedExecutor()

    # 创建主机节点
    host_node = HostNode(
        "host_node",
        devices_config,
        resources_config,
        graph,
        controllers_config,
        bridges,
        discovery_interval,
    )

    executor.add_node(host_node)
    # run_event_loop_in_thread()

    try:
        executor.spin()
    except Exception as e:
        logger.error(traceback.format_exc())
        print(f"Exception caught: {e}")
    finally:
        exit()


def slave(
    devices_config: Dict[str, Any] = {},
    resources_config=[],
    graph: Optional[Dict[str, Any]] = None,
    controllers_config: Dict[str, Any] = {},
    bridges: List[Any] = [],
    args: List[str] = ["--log-level", "debug"],
) -> None:
    """从节点函数"""
    rclpy.init(args=args)
    rclpy.__executor = executor = MultiThreadedExecutor()

    for device_id, device_config in devices_config.items():
        d = initialize_device_from_dict(device_id, device_config)
        if d is None:
            continue
        # 默认初始化
        # if d is not None and isinstance(d, Node):
        #     executor.add_node(d)
        # else:
        #     print(f"Warning: Device {device_id} could not be initialized or is not a valid Node")

    machine_name = os.popen("hostname").read().strip()
    machine_name = "".join([c if c.isalnum() or c == "_" else "_" for c in machine_name])
    n = Node(f"slaveMachine_{machine_name}", parameter_overrides=[])
    executor.add_node(n)

    if BasicConfig.slave_no_host:
        # 确保ResourceAdd存在
        if "ResourceAdd" in globals():
            rclient = n.create_client(ResourceAdd, "/resources/add")
            rclient.wait_for_service()  # FIXME 可能一直等待，加一个参数

            request = ResourceAdd.Request()
            request.resources = [convert_to_ros_msg(Resource, resource) for resource in resources_config]
            response = rclient.call_async(request)
        else:
            print("Warning: ResourceAdd service not available")

    run_event_loop_in_thread()

    try:
        executor.spin()
    except Exception as e:
        print(f"Exception caught: {e}")
    finally:
        exit()


if __name__ == "__main__":
    main()
