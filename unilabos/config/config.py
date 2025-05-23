#!/usr/bin/env python
# coding=utf-8
# 定义配置变量和加载函数
import traceback
import os
import importlib.util
from unilabos.utils import logger


class BasicConfig:
    ENV = "pro"  # 'test'
    config_path = ""
    is_host_mode = True  # 从registry.py移动过来
    slave_no_host = False  # 是否跳过rclient.wait_for_service()


# MQTT配置
class MQConfig:
    lab_id = ""
    instance_id = ""
    access_key = ""
    secret_key = ""
    group_id = ""
    broker_url = ""
    port = 1883
    ca_content = ""
    cert_content = ""
    key_content = ""

    # 指定
    ca_file = ""
    cert_file = ""
    key_file = ""


# OSS上传配置
class OSSUploadConfig:
    api_host = ""
    authorization = ""
    init_endpoint = ""
    complete_endpoint = ""
    max_retries = 3


# HTTP配置
class HTTPConfig:
    remote_addr = "http://127.0.0.1:48197/api/v1"


# ROS配置
class ROSConfig:
    modules = [
        "std_msgs.msg",
        "geometry_msgs.msg",
        "control_msgs.msg",
        "control_msgs.action",
        "nav2_msgs.action",
        "unilabos_msgs.msg",
        "unilabos_msgs.action",
    ]


def _update_config_from_module(module):
    for name, obj in globals().items():
        if isinstance(obj, type) and name.endswith("Config"):
            if hasattr(module, name) and isinstance(getattr(module, name), type):
                for attr in dir(getattr(module, name)):
                    if not attr.startswith("_"):
                        setattr(obj, attr, getattr(getattr(module, name), attr))
    # 更新OSS认证
    if len(OSSUploadConfig.authorization) == 0:
        OSSUploadConfig.authorization = f"lab {MQConfig.lab_id}"
    # 对 ca_file cert_file key_file 进行初始化
    if len(MQConfig.ca_content) == 0:
        # 需要先判断是否为相对路径
        if MQConfig.ca_file.startswith("."):
            MQConfig.ca_file = os.path.join(BasicConfig.config_path, MQConfig.ca_file)
        with open(MQConfig.ca_file, "r", encoding="utf-8") as f:
            MQConfig.ca_content = f.read()
    if len(MQConfig.cert_content) == 0:
        # 需要先判断是否为相对路径
        if MQConfig.cert_file.startswith("."):
            MQConfig.cert_file = os.path.join(BasicConfig.config_path, MQConfig.cert_file)
        with open(MQConfig.cert_file, "r", encoding="utf-8") as f:
            MQConfig.cert_content = f.read()
    if len(MQConfig.key_content) == 0:
        # 需要先判断是否为相对路径
        if MQConfig.key_file.startswith("."):
            MQConfig.key_file = os.path.join(BasicConfig.config_path, MQConfig.key_file)
        with open(MQConfig.key_file, "r", encoding="utf-8") as f:
            MQConfig.key_content = f.read()


def load_config(config_path=None):
    # 如果提供了配置文件路径，从该文件导入配置
    if config_path:
        BasicConfig.config_path = os.path.abspath(os.path.dirname(config_path))
        if not os.path.exists(config_path):
            logger.error(f"配置文件 {config_path} 不存在")
            return

        try:
            module_name = "lab_" + os.path.basename(config_path).replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, config_path)
            if spec is None:
                logger.error(f"配置文件 {config_path} 错误")
                return
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)  # type: ignore
            _update_config_from_module(module)
            logger.info(f"配置文件 {config_path} 加载成功")
        except Exception as e:
            logger.error(f"加载配置文件 {config_path} 失败: {e}")
            traceback.print_exc()
            exit(1)
    else:
        try:
            import unilabos.config.local_config as local_config  # type: ignore

            _update_config_from_module(local_config)
            logger.info("已加载默认配置 unilabos.config.local_config")
        except ImportError:
            pass
