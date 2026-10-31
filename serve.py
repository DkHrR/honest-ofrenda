import ofrenda.engine
import ofrenda.pipeline
from ofrenda.engine import write_remembrance
from ofrenda.pipeline import run_all
from ofrenda.webapp import create_app


def make_app():
    """Wire pipeline and engine to create web app."""
    return create_app(run_fn=lambda text: run_all(text, write_remembrance))


if __name__ == "__main__":
    app = make_app()
    app.run(host="127.0.0.1", port=5000)
