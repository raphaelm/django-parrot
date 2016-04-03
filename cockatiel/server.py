import asyncio

from aiohttp import web

from . import config, replication, handlers


def create_app(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/_status', handlers.status)
    app.router.add_route('GET', '/{name:.+}', handlers.get_file)
    app.router.add_route('PUT', '/{name:.+}', handlers.put_file)
    app.router.add_route('DELETE', '/{name:.+}', handlers.delete_file)
    app.router.add_route('HEAD', '/{name:.+}', handlers.get_file)
    return app


def run(cmdargs=None):
    if cmdargs:
        config.args = config.parser.parse_args(args=cmdargs)
    else:
        config.args = config.parser.parse_args()

    loop = asyncio.get_event_loop()
    start_replication_workers(loop)
    app = create_app(loop)
    web.run_app(app, port=config.args.port, host=config.args.host)
    stop_replication_workers(loop)


def start_replication_workers(loop):
    replication.running = True
    for node in replication.get_nodes():
        loop.create_task(replication.replication_worker(node))


def stop_replication_workers(loop):
    replication.running = False
