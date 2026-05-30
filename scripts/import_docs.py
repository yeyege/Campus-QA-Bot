"""
文档导入工具 - 支持 TXT/Word/PDF/Markdown
用法: python scripts/import_docs.py <文档路径> [分类名称]

示例:
  python scripts/import_docs.py my_faq.txt 选课指南
  python scripts/import_docs.py docs/图书馆规则.pdf 图书馆
"""
import os
import sys
import re

# 设置环境变量
os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def read_txt(file_path):
    """读取TXT文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_markdown(file_path):
    """读取Markdown文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def read_word(file_path):
    """读取Word文件"""
    try:
        import docx
        doc = docx.Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    except ImportError:
        print("错误: 请先安装 python-docx: pip install python-docx")
        sys.exit(1)


def read_pdf(file_path):
    """读取PDF文件"""
    try:
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except ImportError:
        print("错误: 请先安装 PyPDF2: pip install PyPDF2")
        sys.exit(1)


def parse_qa_content(content):
    """解析问答内容，支持多种格式"""
    qa_pairs = []

    # 格式1: Q: xxx\nA: xxx
    pattern1 = r"[Qq][：:]\s*(.*?)\n[Aa][：:]\s*(.*?)(?=\n[Qq][：:]|\n##|\Z)"
    matches1 = re.findall(pattern1, content, re.DOTALL)
    for q, a in matches1:
        q = q.strip()
        a = a.strip()
        if q and a:
            qa_pairs.append((q, a))

    # 格式2: ### 问题\n答案
    if not qa_pairs:
        pattern2 = r"###\s*(.*?)\n(.*?)(?=\n###|\n##|\Z)"
        matches2 = re.findall(pattern2, content, re.DOTALL)
        for q, a in matches2:
            q = q.strip()
            a = a.strip()
            if q and a:
                qa_pairs.append((q, a))

    # 格式3: 按段落分割（如果没找到问答格式）
    if not qa_pairs:
        paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
        for i, para in enumerate(paragraphs):
            if para:
                # 将整个段落作为一个条目
                qa_pairs.append((f"关于{para[:20]}...", para))

    return qa_pairs


def import_to_knowledge_base(file_path, category=None):
    """导入文档到知识库"""
    # 获取文件名和分类
    filename = os.path.basename(file_path)
    if category is None:
        category = os.path.splitext(filename)[0]

    print(f"导入文件: {filename}")
    print(f"分类名称: {category}")

    # 读取文件
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".txt":
        content = read_txt(file_path)
    elif ext == ".md":
        content = read_markdown(file_path)
    elif ext == ".docx":
        content = read_word(file_path)
    elif ext == ".pdf":
        content = read_pdf(file_path)
    else:
        print(f"错误: 不支持的文件格式 {ext}")
        print("支持的格式: .txt, .md, .docx, .pdf")
        return

    # 解析问答
    qa_pairs = parse_qa_content(content)
    print(f"解析到 {len(qa_pairs)} 个问答对")

    if not qa_pairs:
        print("警告: 未找到问答内容，请检查文档格式")
        return

    # 生成Markdown格式并保存
    md_content = f"# {category}\n\n"
    for q, a in qa_pairs:
        md_content += f"### Q: {q}\nA: {a}\n\n"

    output_path = f"knowledge_base/faq/{category}.md"
    os.makedirs("knowledge_base/faq", exist_ok=True)

    # 如果文件已存在，追加内容
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            existing = f.read()
        md_content = existing + "\n" + md_content
        print(f"追加到已有文件: {output_path}")
    else:
        print(f"创建新文件: {output_path}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"导入完成！")

    # 询问是否重新构建向量库
    rebuild = input("是否立即重新构建向量库？(y/n): ").strip().lower()
    if rebuild == "y":
        print("\n重新构建向量库...")
        from src.core.knowledge_loader import KnowledgeLoader
        loader = KnowledgeLoader()
        loader.build_knowledge_base()


def batch_import(directory, category=None):
    """批量导入目录下所有文档"""
    supported_ext = [".txt", ".md", ".docx", ".pdf"]

    for filename in os.listdir(directory):
        ext = os.path.splitext(filename)[1].lower()
        if ext in supported_ext:
            file_path = os.path.join(directory, filename)
            import_to_knowledge_base(file_path, category)
            print("-" * 40)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  单个文件: python scripts/import_docs.py <文件路径> [分类名称]")
        print("  批量导入: python scripts/import_docs.py --batch <目录路径>")
        print("\n示例:")
        print("  python scripts/import_docs.py my_faq.txt 选课指南")
        print("  python scripts/import_docs.py --batch ./my_docs")
        sys.exit(1)

    if sys.argv[1] == "--batch":
        # 批量导入模式
        if len(sys.argv) < 3:
            print("错误: 请指定目录路径")
            sys.exit(1)
        batch_import(sys.argv[2])
    else:
        # 单文件导入模式
        file_path = sys.argv[1]
        category = sys.argv[2] if len(sys.argv) > 2 else None
        import_to_knowledge_base(file_path, category)
