from langchain_community.document_loaders import WebBaseLoader
from typing import List, Tuple
from markitdown import MarkItDown
from langchain_core.documents import Document
import html2text


class DocLoader:
    def __init__(self, doc_type: str, doc_path: List[str]):
        self.doc_path = doc_path
        self.doc_type = doc_type

    def load(self):
        if self.doc_type == "url":
            if len(self.doc_path) > 0:
                return self.load_url()
            else:
                raise ValueError(f"请提供有效的文档,当前文档地址无效: {self.doc_path}")
        elif self.doc_type == "file":
            if len(self.doc_path) > 0:
                return self.load_file()
            else:
                raise ValueError(f"请提供有效的文档,当前文档地址无效: {self.doc_path}")
        else:
            raise ValueError(f"Unsupported document type: {self.doc_type}")

    def load_url(self) -> Tuple[List[Document], List[dict]]:
        result_docs = []
        error_urls = []
        for url in self.doc_path:
            try:
                docs = WebBaseLoader(web_path=url).load()
                for doc in docs:
                    try:
                        doc.page_content = html2text.html2text(doc.page_content)
                        doc.metadata = {"source": url}
                        # print("doc metadata: ", doc.metadata)
                        result_docs.append(doc)
                    except Exception as e:
                        error_urls.append(
                            {"file_path": doc.metadata["source"], "error": e}
                        )
                        continue
            except Exception as e:
                error_urls.append({"file_path": url, "error": e})
                continue
        return (result_docs, error_urls)

    def load_file(self) -> Tuple[List[Document], List[dict]]:
        docs = []
        error_files = []
        for file_path in self.doc_path:
            try:
                md = MarkItDown()
                result = md.convert(file_path)
                docs.append(
                    Document(
                        page_content=result.text_content, metadata={"source": file_path}
                    )
                )
            except (OSError, IOError, ValueError, TypeError) as e:
                error_files.append({"file_path": file_path, "error": e})
                continue

        return (docs, error_files)


if __name__ == "__main__":
    loader = DocLoader(
        "url",
        [
            "https://lilianweng.github.io/posts/2023-06-23-agent/",  # AI代理相关文章
            # "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",  # 提示工程文章
            # "https://lilianweng.github.io/posts/2023-10-25-adv-attack-llm/",  # LLM对抗攻击文章
        ],
    )
    docs, error_urls = loader.load()
    print(len(docs))
    # print(len(error_urls))
    # print(len(docs[0].page_content))
