import argparse
import uvicorn
import os


def main():
    parser = argparse.ArgumentParser(description="运行 FastAPI 应用程序。")
    parser.add_argument("--dev", action="store_true", help="启用带热重载的开发模式。")
    parser.add_argument(
        "--host", type=str, default="0.0.0.0", help="监听的主机地址 (默认: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="监听的端口 (默认: 8000)"
    )

    args = parser.parse_args()

    if args.dev:
        print(f"🚀 正在以【开发模式】启动 (热重载已开启)...")
        print(f"🔗 访问地址: http://{args.host}:{args.port}")
        # 在开发模式下，通常会自动设置环境变量，便于应用内部根据环境做逻辑区分
        os.environ["ENV"] = "development"
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)
    else:
        print(f"✅ 正在以【生产模式】启动...")
        print(f"🔗 访问地址: http://{args.host}:{args.port}")
        os.environ["ENV"] = "production"
        uvicorn.run("app.main:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
