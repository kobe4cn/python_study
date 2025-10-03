import redis

r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

print("=== Redis 中的所有 key ===")
keys = r.keys("*")
print(f"找到 {len(keys)} 个 key: {keys}")

print("\n=== 每个 key 的值 ===")
for key in keys:
    value = r.get(key)
    print(f"Key: '{key}' -> Value: '{value}'")
    print(f"Key 类型: {type(key)}, Key 长度: {len(key)}")
    print(f"Key 的字节表示: {key.encode()}")
    print("-" * 50)
