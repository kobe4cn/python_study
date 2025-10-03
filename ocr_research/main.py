from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document
from typing import Union, List
from paddleocr import PaddleOCR
import os


class ImageOCRReader(BaseReader):
    """使用 PP-OCR v5 从图像中提取文本并返回 Document"""

    def __init__(self, lang="ch", use_gpu=False, **kwargs):
        """
        Args:
            lang: OCR 语言 ('ch', 'en', 'fr', etc.)
            use_gpu: 是否使用 GPU 加速
            **kwargs: 其他传递给 PaddleOCR 的参数
        """

        self.lang = lang
        self.gpu = "cpu"
        if use_gpu:
            self.gpu = "gpu"
        self.ocr = PaddleOCR(
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
            lang=self.lang,
            device=self.gpu,
        )

    def load_data(self, file: Union[str, List[str]]) -> List[Document]:
        """
        从单个或多个图像文件中提取文本，返回 Document 列表
        Args:
            file: 图像路径字符串 或 路径列表
        Returns:
            List[Document]
        """
        # 确保输入是列表格式
        if isinstance(file, str):
            files = [file]
        else:
            files = file

        documents = []

        for file_path in files:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                print(f"警告: 文件不存在 - {file_path}")
                continue

            # 检查文件扩展名
            supported_extensions = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"]
            file_ext = os.path.splitext(file_path)[1].lower()
            if file_ext not in supported_extensions:
                print(f"警告: 不支持的文件格式 - {file_path}")
                continue

            try:
                # 执行OCR识别
                result = self.ocr.predict(file_path)

                # 提取文本内容
                text_content = []
                avg_confidence = 0.0
                if result and result[0]:
                    for res in result[0]["rec_texts"]:
                        text_content.append(res)
                    avg_confidence = sum(result[0]["rec_scores"]) / len(
                        result[0]["rec_scores"]
                    )
                # 合并所有文本
                full_text = "\n".join(text_content) if text_content else ""

                # 创建Document对象
                doc = Document(
                    text=full_text,
                    metadata={
                        "image_path": file_path,
                        "ocr_model": "PP-OCRv5",
                        "language": self.lang,
                        "num_text_blocks": len(result[0]),
                        "avg_confidence": avg_confidence,
                    },
                )
                documents.append(doc)

            except Exception as e:
                print(f"OCR处理文件 {file_path} 时出错: {str(e)}")
                continue

        return documents
