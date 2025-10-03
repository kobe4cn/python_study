"""诊断 Agent 调用工具时参数传递的问题"""
from react_agent_test import get_order_status_tool, add_order_status
import redis
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

print("=" * 60)
print("步骤 1: 添加测试数据到 Redis")
print("=" * 60)

test_orders = [
    {"order_id": "00123456", "order_status": "已发货"},
    {"order_id": "00123459", "order_status": "配送中"},
]

success = add_order_status(test_orders)
print(f"添加数据结果: {success}\n")

print("=" * 60)
print("步骤 2: 检查 Redis 中的实际数据")
print("=" * 60)

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
keys = r.keys("*")
print(f"找到 {len(keys)} 个 key: {keys}")

for key in keys:
    value = r.get(key)
    print(f"  Key: '{key}' (type: {type(key).__name__}, len: {len(key)})")
    print(f"  Value: '{value}'")
    print(f"  Key bytes: {repr(key)}")
    print()

print("=" * 60)
print("步骤 3: 直接调用工具函数测试")
print("=" * 60)

test_cases = [
    "00123456",
    "00123459",
    " 00123456",  # 带前导空格
    "00123456 ",  # 带后导空格
    " 00123456 ",  # 带两侧空格
]

for order_id in test_cases:
    print(f"\n测试输入: '{order_id}' (len: {len(order_id)})")
    result = get_order_status_tool.invoke({"order_id": order_id})
    print(f"返回结果: {result}")

print("\n" + "=" * 60)
print("步骤 4: 模拟 Agent 可能传递的参数格式")
print("=" * 60)

# Agent 可能会这样解析参数
agent_inputs = [
    {"order_id": "00123456"},
    {"order_id": " 00123456"},
    {"order_id": "查询订单状态 00123456"},  # 可能包含问题文本
    {"order_id": "00123456\n"},  # 可能包含换行符
]

for input_dict in agent_inputs:
    order_id = input_dict["order_id"]
    print(f"\n测试输入: '{order_id}'")
    result = get_order_status_tool.invoke(input_dict)
    print(f"返回结果: {result}")
