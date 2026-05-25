from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # 应用配置
    app_name: str = "clouddesk-agent"
    app_env: str = "dev"
    debug: bool = False
    log_level: str = "INFO"

    # 数据库配置
    database_url: str = "postgresql+psycopg2://postgres:123456@localhost:5432/clouddesk"
    auto_create_tables: bool = True

    # Java 后端配置
    java_service_url: str = "http://localhost:8101"
    java_internal_token: str = "clouddesk-internal-token"

    # LLM 配置
    openai_api_key: str = ""
    openai_base_url: str = ""
    llm_model_fast: str = "gpt-4o-mini"
    llm_model_medium: str = "gpt-4o"
    llm_model_strong: str = "gpt-4o"

    # RAG 配置
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    embedding_model: str = "text-embedding-v4"
    embedding_dimension: int = 1024
    rag_top_k: int = 5

    # Agent 配置
    max_handoff_count: int = 2

    # 文件存储配置
    storage_root: str = "instance/storage"
    max_upload_size_mb: int = 10
    upload_allowed_extensions: str = "jpg,jpeg,png,gif,webp,pdf,txt,csv,xlsx"
    upload_scene_dirs: str = "default:uploads,avatar:avatars,document:documents"

    # 表格数据配置
    tabular_allowed_extensions: str = "csv,xlsx"

    # PDF 配置
    pdf_default_font: str = "Helvetica"


settings = Settings()
