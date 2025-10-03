"""
向量存储主类
"""

import enum
from typing import List
from doc.vstore.qdrant_vector_store_client import QdrantVectorStoreClient
from langchain_core.documents import Document

VECTOR_STORE_PROVIDER = enum.Enum(
    "VECTOR_STORE_PROVIDER", ["REDIS", "QDRANT", "MILVUS", "Pgvector"]
)

"""
向量存储主类
"""


class VStoreMain:
    def __init__(
        self,
        vector_store_provider: VECTOR_STORE_PROVIDER,
        collection_name: str,
        host: str,
        port: int,
        user: str,
        password: str,
        embedding_model: str,
        top_k: int,
    ):
        self.vector_store_provider = vector_store_provider
        self.collection_name = collection_name
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.embedding_model = embedding_model
        self.top_k = top_k
        self.vstore = self._init_vstore()

    def _init_vstore(self):
        """初始化向量存储客户端"""
        if self.vector_store_provider == VECTOR_STORE_PROVIDER.QDRANT:
            return QdrantVectorStoreClient(
                collection_name=self.collection_name,
                host=self.host,
                port=self.port,
                _user=self.user,
                _password=self.password,
                embedding_model=self.embedding_model,
                top_k=self.top_k,
            )
        else:
            raise ValueError(
                f"Unsupported vector store provider: {self.vector_store_provider}"
            )

    def add_documents(self, documents: List[Document]):
        """添加文档到向量存储"""
        return self.vstore.add_documents(documents)

    def search(self, query: str):
        """搜索相似文档"""
        return self.vstore.search(query)

    def as_retriever(self):
        """获取检索器对象"""
        return self.vstore.as_retriever()

    def upsert_documents(self, documents: List[Document]):
        """更新或插入文档"""
        return self.vstore.upsert_documents(documents)

    # def add_document(self, document: Document):
    #     self.vstore.add_document(document)

    # def search(self, query: str):
    #     return self.vstore.search(query)


if __name__ == "__main__":
    # from doc.loader.doc_loader import DocLoader
    # from doc.spliter.md_splitter import MdSplitter

    # loader = DocLoader(
    #     "url",
    #     [
    #         "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
    #         # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
    #         # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
    #     ],
    # )
    # docs, error_urls = loader.load()
    # md_splitter = MdSplitter(
    #     headers=[
    #         ("#", "Header 1"),
    #         ("##", "Header 2"),
    #         ("###", "Header 3"),
    #         ("####", "Header 4"),
    #         ("#####", "Header 5"),
    #         ("######", "Header 6"),
    #     ],
    #     tokenizer_name="huggingface",
    #     encoding_name="Qwen/Qwen-7B-Chat",
    #     chunk_size=1000,
    #     chunk_overlap=200,
    #     keep_separator=True,
    # )
    # # md_splitter = MdSplitter(
    # #     headers=[
    # #         ("#", "Header 1"),
    # #         ("##", "Header 2"),
    # #         ("###", "Header 3"),
    # #         ("####", "Header 4"),
    # #         ("#####", "Header 5"),
    # #         ("######", "Header 6"),
    # #     ],
    # #     tokenizer_name="tiktoken",
    # #     encoding_name="cl100k_base",
    # #     chunk_size=1000,
    # #     chunk_overlap=200,
    # #     keep_separator=True,
    # # )
    # result = md_splitter.split(docs)
    vstore = VStoreMain(
        vector_store_provider=VECTOR_STORE_PROVIDER.QDRANT,
        collection_name="document_store",
        host="localhost",
        port=6333,
        user="",
        password="",
        embedding_model="text-embedding-v4",
        top_k=3,
    )
    # ids = vstore.add_documents(result)
    # print(ids)
    search_result = vstore.search("什么是AI代理？")
    print(len(search_result))
    print(search_result[0].page_content)
