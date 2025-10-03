```mermaid
flowchart LR
  subgraph Client[前端 Chat UI]
    A[用户输入/上传] --> B[SSE/WS 渲染流式回复]
  end

  subgraph Edge[API 网关/边车]
    C[鉴权/AK·SK/App Token]
    D[限流/重试/审计/敏感词]
  end

  subgraph Bailian[阿里云百炼（Model Studio）]
    E[应用调用\n(智能体/编排/工作流)]
    F[知识库RAG检索\n(云端知识索引)]
  end

  subgraph Data[数据与可观测]
    G[对象存储/文档源]
    H[日志/指标/Tracing]
    I[配置&密钥管控]
  end

  A -->|HTTPS| C --> D -->|调用应用(HTTP/SSE 或 SDK)| E
  E -->|检索| F -->|召回/重排/引用| E -->|流式Token| B
  G -->|增量构建| F
  D --> H
  I --> C

```
```mermaid
flowchart TD
    A[知识文件导入/上传] --> B[数据分片与预处理]
    B --> C[Embedding向量生成]
    C --> D[向量入库（Milvus/ADB PG）]
    D --> E[构建索引/元数据归档]
    E --> F[检索服务API（语义/关键词/混合）]
    F --> G[相关知识片段召回]
    G --> H[大模型推理服务（通义千问/GPT/PAI-EAS）]
    H --> I[融合召回内容/生成答案]
    I --> J[前端/业务系统接口输出]
    J --> K[效果反馈/溯源展示]

```