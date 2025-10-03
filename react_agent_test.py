from langchain_community.tools import DuckDuckGoSearchRun, DuckDuckGoSearchResults
from langchain.tools import tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import List, Dict
import redis
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def add_order_status(order_id: List[Dict[str, str]]) -> bool:
    """
    Add an order status to redis with the given ID.

    Args:
        order_id (str): The ID of the order to add the status to.
        order_status (str): The status to add to the order.

    Returns:
        str: A message indicating that the order status has been added.
    """
    try:
        if order_id:
            r = redis.Redis(
                host="localhost",
                port=6379,
                db=0,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                decode_responses=True,
            )

            # 测试连接
            r.ping()

            for order in order_id:
                order_id_key = order["order_id"]
                order_status = order["order_status"]
                r.set(order_id_key, order_status)
                r.expire(order_id_key, 60 * 60 * 24 * 7)  # 7天后过期（便于测试）

            logger.info(f"订单状态已添加到redis")
            return True
        else:
            return False
    except Exception as e:
        logger.error(f"添加订单状态失败: {str(e)}")
        return False


def get_order_status(order_id: str) -> str:
    """
    通过订单ID查询订单状态.
    """
    try:
        # 处理可能的字节串输入
        if isinstance(order_id, bytes):
            order_id = order_id.decode("utf-8")

        # 清理输入，移除可能的换行符和多余字符
        order_id = order_id.strip()

        logger.info(f"查询订单状态: {order_id}")

        # 使用连接池和更稳定的连接配置
        r = redis.Redis(
            host="localhost", port=6379, db=0, decode_responses=True  # 自动解码响应
        )

        # 测试连接
        r.ping()

        order_status = r.get(order_id)

        if order_status is None:
            logger.info(f"订单状态: None")
            return "订单不存在"

        logger.info(f"订单状态: {order_status}")
        return order_status
    except redis.ConnectionError as e:
        logger.error(f"Redis连接失败: {str(e)}")
        return "连接失败"
    except redis.TimeoutError as e:
        logger.error(f"Redis超时: {str(e)}")
        return "查询超时"
    except Exception as e:
        logger.error(f"查询订单状态失败: {str(e)}")
        return "查询失败"


search_wrapper = DuckDuckGoSearchResults(output_format="list")


@tool("my_search_tool")
def search_tool(query: str) -> List[str]:
    """
    通过搜索引擎查询.
    """
    result = search_wrapper.invoke(query)
    return [res["snippet"] for res in result]


# logger.info(search_tool.name)
# logger.info(search_tool.description)
# logger.info(search_tool.args)


@tool("get_order_status_tool")
def get_order_status_tool(order_id: str) -> str:
    """
    通过订单ID查询订单状态。只需要提供8位数字的订单ID。

    参数:
        order_id: 8位数字订单号,例如 "00123456"

    返回:
        订单状态字符串
    """
    try:
        # 处理可能的字节串输入
        if isinstance(order_id, bytes):
            order_id = order_id.decode("utf-8")

        # 清理输入,移除可能的换行符和多余字符
        order_id = order_id.strip()

        # 额外清理:只保留数字部分(处理 "00123456\nObserv" 这种情况)
        if not order_id.isdigit():
            import re
            match = re.search(r'\d{8}', order_id)
            if match:
                order_id = match.group(0)
                logger.info(f"从输入中提取到订单号: {order_id}")
            else:
                logger.warning(f"无法从输入提取有效订单号: {repr(order_id)}")
                return f"无效的订单号格式"

        logger.info(f"工具调用 - 查询订单状态: {order_id}")

        # 直接在这里实现Redis查询,避免调用其他函数
        r = redis.Redis(
            host="localhost", port=6379, db=0, decode_responses=True  # 自动解码为字符串
        )

        # 测试连接
        r.ping()
        logger.info("Redis连接测试成功")

        order_status = r.get(order_id)
        logger.info(f"Redis查询结果: {order_status}")

        if order_status is None:
            logger.info(f"订单 {order_id} 不存在")
            return f"订单 {order_id} 不存在"

        logger.info(f"订单 {order_id} 状态: {order_status}")
        return f"订单 {order_id} 的状态是: {order_status}"

    except redis.ConnectionError as e:
        logger.error(f"Redis连接失败: {str(e)}")
        return "连接失败"
    except redis.TimeoutError as e:
        logger.error(f"Redis超时: {str(e)}")
        return "查询超时"
    except Exception as e:
        logger.error(f"查询订单状态失败: {str(e)}")
        return f"查询失败: {str(e)}"


import os
import dotenv
dotenv.load_dotenv()
def get_api_key():
    api_key=os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("未找到OPENAI_API_KEY环境变量")
    return api_key

def get_base_url():
    base_url=os.getenv("OPENAI_BASE_URL")
    if not base_url:
        raise ValueError("未找到OPENAI_BASE_URL环境变量")
    return base_url


def create_react_search_agent() -> AgentExecutor:
    tools = [search_tool, get_order_status_tool]
    llm = ChatOpenAI(
        model="qwen3-max", temperature=0.3, api_key=get_api_key(), base_url=get_base_url()
    )
    prompt = PromptTemplate.from_template(
        """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format EXACTLY:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action (ONLY the parameter value, nothing else)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

IMPORTANT:
- Action Input must be ONLY the parameter value
- For get_order_status_tool, Action Input should be ONLY the order ID (e.g., "00123456")
- Do NOT include any extra text or newlines in Action Input

Begin!

Question: {input}
Thought:{agent_scratchpad}"""
    )
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=10,
        handle_parsing_errors=True,
    )


def main():
    agent = create_react_search_agent()
    questions = ["查询订单状态 00123456", "查询快递状态 00123459","查询订单状态 00123470"]
    for question in questions:
        result = agent.invoke({"input": question})
        print(result["output"])
        print("-"*50)

if __name__ == "__main__":
    main()