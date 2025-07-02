from huggingface_hub import snapshot_download, HfApi
import os


def robust_download_model(
        model_name: str,
        target_dir: str,
        max_retries: int = 3,
        timeout: int = 60,
        proxy: str = "http://127.0.0.1:7890"
):
    """
    增强版模型下载函数（自动重试+代理支持）

    参数:
        model_name: 模型ID (如 "Qwen/Qwen1.5-0.5B")
        target_dir: 目标存储目录
        max_retries: 最大重试次数
        timeout: 单次请求超时(秒)
        proxy: 代理地址 (如 "http://127.0.0.1:1080")
    """
    # 环境设置
    os.makedirs(target_dir, exist_ok=True)
    if proxy:
        os.environ["HTTP_PROXY"] = proxy
        os.environ["HTTPS_PROXY"] = proxy

    # 验证模型是否存在
    try:
        api = HfApi()
        model_info = api.model_info(model_name, timeout=timeout)
        print(f"🔄 开始下载 {model_name} (共 {len(model_info.siblings)} 个文件)")
    except Exception as e:
        raise ValueError(f"无法获取模型信息: {e}")

    # 带重试的下载
    for attempt in range(max_retries):
        try:
            path = snapshot_download(
                repo_id=model_name,
                local_dir=target_dir,
                local_dir_use_symlinks="auto",
                resume_download=True,
            )
            print(f"\n✅ 下载成功！模型保存到: {path}")
            return path
        except Exception as e:
            print(f"\n⚠️ 第 {attempt + 1} 次尝试失败: {str(e)}")
            if attempt == max_retries - 1:
                raise ConnectionError(f"❌ 下载失败（已重试 {max_retries} 次）")
            print(f"⏳ 10秒后重试...")
            return None
    return None


# 使用示例
if __name__ == "__main__":
    try:
        robust_download_model(
            model_name="Qwen/Qwen1.5-0.5B",  # 更小的模型测试
            target_dir="./qwen_model",
            proxy="http://127.0.0.1:7890"  # 根据实际情况修改或删除
        )
    except Exception as e:
        print(f"\n❌ 最终失败: {e}")
        print("\n💡 手动解决方案：")
        print("1. 直接从官网下载: https://huggingface.co/Qwen/Qwen1.5-0.5B")
        print("2. 使用git命令: git lfs install && git clone https://huggingface.co/Qwen/Qwen1.5-0.5B")