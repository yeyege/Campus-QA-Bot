"""
知识库加载与向量化模块
读取FAQ文档，分割成chunks，存入ChromaDB
"""
import os
import re
from typing import List, Tuple

import chromadb

# 使用HuggingFace镜像（国内访问）
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"


class KnowledgeLoader:
    def __init__(self, faq_dir: str = "knowledge_base/faq", persist_dir: str = "knowledge_base/processed"):
        self.faq_dir = faq_dir
        self.persist_dir = persist_dir
        self.embedding_model = None
        self.client = None
        self.collection = None

    def load_embedding_model(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        """加载Embedding模型（使用全局缓存）"""
        from src.core.cache import get_embedding_model
        self.embedding_model = get_embedding_model()

    def init_chromadb(self, collection_name: str = "campus_faq"):
        """初始化ChromaDB"""
        os.makedirs(self.persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=self.persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def parse_markdown(self, file_path: str) -> List[Tuple[str, str]]:
        """解析Markdown文件，提取问答对"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        qa_pairs = []
        # 匹配 Q: ... A: ... 格式
        pattern = r"###\s*Q:\s*(.*?)\nA:\s*(.*?)(?=\n###|\n##|\Z)"
        matches = re.findall(pattern, content, re.DOTALL)

        for question, answer in matches:
            question = question.strip()
            answer = answer.strip()
            if question and answer:
                qa_pairs.append((question, answer))

        return qa_pairs

    def load_all_faqs(self) -> List[Tuple[str, str, str]]:
        """加载所有FAQ文件"""
        all_qa = []
        for filename in os.listdir(self.faq_dir):
            if filename.endswith(".md"):
                file_path = os.path.join(self.faq_dir, filename)
                category = filename.replace(".md", "")
                qa_pairs = self.parse_markdown(file_path)
                for q, a in qa_pairs:
                    all_qa.append((category, q, a))
        return all_qa

    def build_knowledge_base(self):
        """构建知识库"""
        print("=" * 50)
        print("开始构建知识库")
        print("=" * 50)

        # 加载模型
        self.load_embedding_model()

        # 初始化ChromaDB
        self.init_chromadb()

        # 清空旧数据
        try:
            self.client.delete_collection("campus_faq")
            self.collection = self.client.get_or_create_collection(
                name="campus_faq",
                metadata={"hnsw:space": "cosine"}
            )
        except:
            pass

        # 加载FAQ
        print("\n加载FAQ文档...")
        all_qa = self.load_all_faqs()
        print(f"\n共加载 {len(all_qa)} 个问答对")

        if not all_qa:
            print("没有找到FAQ数据，请检查 knowledge_base/faq/ 目录")
            return

        # 生成向量并存储
        print("\n生成向量并存储...")
        ids = []
        documents = []
        metadatas = []
        embeddings = []

        for i, (category, question, answer) in enumerate(all_qa):
            # 文档内容 = 问题 + 答案
            doc = f"问题：{question}\n答案：{answer}"

            ids.append(f"faq_{i}")
            documents.append(doc)
            metadatas.append({"category": category, "question": question})

        # 批量生成向量
        doc_embeddings = self.embedding_model.encode(documents)
        embeddings = doc_embeddings.tolist()

        # 存入ChromaDB
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(f"\n知识库构建完成！共 {len(ids)} 条记录")
        print(f"存储位置: {os.path.abspath(self.persist_dir)}")

    def search(self, query: str, top_k: int = 3) -> List[dict]:
        """检索相关文档"""
        if self.collection is None:
            self.init_chromadb()
        if self.embedding_model is None:
            self.load_embedding_model()

        query_embedding = self.embedding_model.encode([query]).tolist()

        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        search_results = []
        for i in range(len(results["ids"][0])):
            search_results.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })

        return search_results


if __name__ == "__main__":
    loader = KnowledgeLoader()
    loader.build_knowledge_base()

    # 测试检索
    print("\n" + "=" * 50)
    print("测试检索")
    print("=" * 50)

    query = "食堂几点开门？"
    results = loader.search(query, top_k=2)

    for r in results:
        print(f"\n[{r['metadata']['category']}] 相似度: {1 - r['distance']:.4f}")
        print(r["document"])
