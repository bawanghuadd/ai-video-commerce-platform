from pathlib import Path

from fastapi.routing import APIRoute

from app.main import fastapi_app


APP_ROOT = Path(__file__).resolve().parents[2] / "app"


def read_python_files(directory: str):
    for path in (APP_ROOT / directory).glob("*.py"):
        yield path, path.read_text(encoding="utf-8")


def test_routers_do_not_access_orm_or_transactions():
    for path, source in read_python_files("api"):
        assert "app.models" not in source, path
        assert ".commit(" not in source, path
        assert ".rollback(" not in source, path


def test_repositories_do_not_commit_or_build_http_responses():
    for path, source in read_python_files("repositories"):
        assert ".commit(" not in source, path
        assert "HTTPException" not in source, path
        assert "JSONResponse" not in source, path


def test_services_do_not_depend_on_fastapi():
    for path, source in read_python_files("services"):
        assert "HTTPException" not in source, path
        assert "from fastapi" not in source, path


def test_single_production_session_and_security_implementations():
    sources = {
        path: path.read_text(encoding="utf-8")
        for path in APP_ROOT.rglob("*.py")
    }
    engine_factories = [path for path, source in sources.items() if "create_engine(" in source]
    session_factories = [path for path, source in sources.items() if "sessionmaker(" in source]
    password_factories = [
        path for path, source in sources.items() if "PasswordHash.recommended()" in source
    ]
    assert [path.relative_to(APP_ROOT).as_posix() for path in engine_factories] == [
        "database/session.py"
    ]
    assert [path.relative_to(APP_ROOT).as_posix() for path in session_factories] == [
        "database/session.py"
    ]
    assert [path.relative_to(APP_ROOT).as_posix() for path in password_factories] == [
        "core/security.py"
    ]


def test_business_routes_declare_response_models():
    business_prefixes = (
        "/api/auth",
        "/api/products",
        "/api/content-analyses",
        "/api/scripts",
        "/api/video-tasks",
        "/api/knowledge-items",
        "/api/system-settings",
    )
    def walk_routes(routes):
        for route in routes:
            included_router = getattr(route, "original_router", None)
            if included_router is not None:
                yield from walk_routes(included_router.routes)
            elif hasattr(route, "response_model"):
                yield route

    routes = [
        route
        for route in walk_routes(fastapi_app.routes)
        if route.path.startswith(business_prefixes)
    ]
    assert routes
    assert all(route.response_model is not None for route in routes)
