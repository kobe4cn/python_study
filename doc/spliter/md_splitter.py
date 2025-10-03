from langchain_text_splitters import (
    ExperimentalMarkdownSyntaxTextSplitter,
    MarkdownTextSplitter,
    TextSplitter,
)
from langchain_core.documents import Document
from typing import List
from transformers import AutoTokenizer


class MdSplitter:
    def __init__(
        self,
        headers: List[tuple[str, str]],
        tokenizer_name: str,
        encoding_name: str,
        chunk_size: int,
        chunk_overlap: int,
        keep_separator: bool = True,
    ):
        self.header_split = ExperimentalMarkdownSyntaxTextSplitter(
            headers_to_split_on=headers
        )
        if tokenizer_name == "tiktoken":
            self.token_splitter: TextSplitter = (
                MarkdownTextSplitter.from_tiktoken_encoder(
                    encoding_name=encoding_name,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    keep_separator=keep_separator,
                )
            )
        else:
            tokenizer = AutoTokenizer.from_pretrained(
                encoding_name, trust_remote_code=True
            )
            self.token_splitter = MarkdownTextSplitter.from_huggingface_tokenizer(
                tokenizer=tokenizer,
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
            )

    def split(self, docs: List[Document]) -> List[Document]:
        if len(docs) == 0:
            raise ValueError("docs is empty")
        splited_docs = []
        for doc in docs:
            # print("doc metadata: ", doc.metadata)
            header_docs = self.header_split.split_text(doc.page_content)
            # 为header_docs添加metadata
            header_docs = [
                Document(page_content=header_doc.page_content, metadata=doc.metadata)
                for header_doc in header_docs
            ]
            # print("head_docs metadata: ", header_docs[0].metadata)
            final_docs = self.token_splitter.split_documents(header_docs)
            # 为final_docs添加metadata
            final_docs = [
                Document(page_content=final_doc.page_content, metadata=doc.metadata)
                for final_doc in final_docs
            ]
            # print("final_docs metadata: ", final_docs[0].metadata)
            splited_docs.extend(final_docs)

        return splited_docs


if __name__ == "__main__":
    from doc.loader.doc_loader import DocLoader

    loader = DocLoader(
        "url",
        [
            "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
            # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
            # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
        ],
    )
    docs, error_urls = loader.load()
    # print(len(docs))
    # print(len(error_urls))
    # print(len(docs[0].page_content))
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
    md_splitter = MdSplitter(
        headers=[
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
            ("#####", "Header 5"),
            ("######", "Header 6"),
        ],
        tokenizer_name="tiktoken",
        encoding_name="cl100k_base",
        chunk_size=1000,
        chunk_overlap=200,
        keep_separator=True,
    )
    result = md_splitter.split(docs)
    print(len(result))
