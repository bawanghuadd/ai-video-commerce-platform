import argparse
import os

from app.database import SessionLocal
from app.services.auth import AuthService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="安全创建或晋升管理员")
    subparsers = parser.add_subparsers(dest="command", required=True)
    create = subparsers.add_parser("create", help="创建管理员")
    create.add_argument("username")
    create.add_argument("--display-name", required=True)
    create.add_argument("--password-env", default="ADMIN_PASSWORD")
    promote = subparsers.add_parser("promote", help="晋升既有用户")
    promote.add_argument("username")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    with SessionLocal() as session:
        service = AuthService(session)
        if args.command == "create":
            password = os.getenv(args.password_env)
            if not password:
                raise SystemExit(f"环境变量 {args.password_env} 未设置")
            service.create_admin(args.username, args.display_name, password)
        else:
            service.promote_admin(args.username)
    print("管理员操作完成")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
