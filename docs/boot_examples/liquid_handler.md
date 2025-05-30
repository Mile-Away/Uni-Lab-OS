# 移液站样例

本样例介绍如何配置和启动移液站设备，并执行基本操作如插入枪头等。

## 准备工作

### 设备配置文件

移液站设备的完整配置可在 `test/experiments/plr_test.json` 文件中找到。该配置文件采用平展结构，通过 `type` 字段区分物料和设备，并通过 `parent` 和 `children` 字段实现层级关系。

配置文件示例片段：

```json
{
  "nodes": [
        {
            "id": "PLR_STATION",
            "name": "PLR_LH_TEST",
            "parent": null,
            "type": "device",
            "class": "liquid_handler",
            "config": {},
            "data": {},
            "children": [
                "deck"
            ]
        },
    {
      "id": "deck",
      "name": "deck",
      "type": "container",
      "class": null,
      "parent": "PLR_STATION",
      "children": [
                "trash",
                "trash_core96",
                "teaching_carrier",
                "tip_rack",
                "plate"
            ]
    }
  ],
  "links": []
}
```

配置文件定义了移液站的组成部分，主要包括：
- 移液站本体（LiquidHandler）- 设备类型
- 移液站携带物料实例（deck）- 物料类型

## 启动方法

### 1. 启动移液站节点

使用以下命令启动移液站设备：

```bash
unilab -g test/experiments/plr_test.json --app_bridges ""
```

### 2. 执行枪头插入操作

启动后，您可以使用以下命令执行插入枪头操作：

```bash
ros2 action send_goal /devices/PLR_STATION/pick_up_tips unilabos_msgs/action/_liquid_handler_pick_up_tips/LiquidHandlerPickUpTips "{ tip_spots: [ { id: 'tip_rack_tipspot_0_0', name: 'tip_rack_tipspot_0_0', sample_id: null, children: [], parent: 'tip_rack', type: 'device', config: { position: { x: 7.2, y: 68.3, z: -83.5 }, size_x: 9.0, size_y: 9.0, size_z: 0, rotation: { x: 0, y: 0, z: 0, type: 'Rotation' }, category: 'tip_spot', model: null, type: 'TipSpot', prototype_tip: { type: 'HamiltonTip', total_tip_length: 95.1, has_filter: true, maximal_volume: 1065, pickup_method: 'OUT_OF_RACK', tip_size: 'HIGH_VOLUME' } }, data: { tip: { type: 'HamiltonTip', total_tip_length: 95.1, has_filter: true, maximal_volume: 1065, pickup_method: 'OUT_OF_RACK', tip_size: 'HIGH_VOLUME' }, tip_state: { liquids: [], pending_liquids: [], liquid_history: [] }, pending_tip: { type: 'HamiltonTip', total_tip_length: 95.1, has_filter: true, maximal_volume: 1065, pickup_method: 'OUT_OF_RACK', tip_size: 'HIGH_VOLUME' } } } ], use_channels: [ 0 ], offsets: [ { x: 0.0, y: 0.0, z: 0.0 } ] }"
```

此命令会通过ros通信触发移液站执行枪头插入操作，得到如下的PyLabRobot的输出日志。

```log
Picking up tips:
pip#  resource             offset           tip type     max volume (µL)  fitting depth (mm)   tip length (mm)  filter    
  p0: tip_rack_tipspot_0_0 0.0,0.0,0.0      HamiltonTip  1065             8                    95.1             Yes  
```

## 常见问题

1. **重复插入枪头不成功**：操作编排应该符合实际操作顺序，可自行通过PyLabRobot进行测试

## 移液站支持的操作

移液站支持多种操作，以下是当前系统支持的操作列表：

1. **LiquidHandlerAspirate** - 吸液操作
2. **LiquidHandlerDispense** - 排液操作
3. **LiquidHandlerDiscardTips** - 丢弃枪头
4. **LiquidHandlerDropTips** - 卸下枪头
5. **LiquidHandlerDropTips96** - 卸下96通道枪头
6. **LiquidHandlerMoveLid** - 移动盖子
7. **LiquidHandlerMovePlate** - 移动板子
8. **LiquidHandlerMoveResource** - 移动资源
9. **LiquidHandlerPickUpTips** - 插入枪头
10. **LiquidHandlerPickUpTips96** - 插入96通道枪头
11. **LiquidHandlerReturnTips** - 归还枪头
12. **LiquidHandlerReturnTips96** - 归还96通道枪头
13. **LiquidHandlerStamp** - 打印标记
14. **LiquidHandlerTransfer** - 液体转移

这些操作可通过ROS2 Action接口进行调用，以实现复杂的移液流程。