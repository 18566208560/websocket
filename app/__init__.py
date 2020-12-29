from flask import Flask
from app.routes import urls
from app.services.pool import ch_pool_init, redis_pool_init
from app.services.response import res_json


def create_app(config):
    app = Flask(__name__)
    app.config.from_object(config)

    # DB
    from app.models import db
    db.init_app(app)
    # mysql group by 查询支持
    with app.app_context():
        db.session.execute("set @@global.sql_mode='STRICT_TRANS_TABLES,"
                           "NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,"
                           "NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';",
                           bind=db.get_engine(app, 'tq30'))
        db.session.execute("set @@global.sql_mode='STRICT_TRANS_TABLES,"
                           "NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,"
                           "NO_AUTO_CREATE_USER,NO_ENGINE_SUBSTITUTION';")

    @app.errorhandler(404)
    @app.errorhandler(405)
    def not_found_handler(e):
        return res_json(code='not_found'), 404

    # @app.errorhandler(Exception)
    # def system_error_shandler(e):
    #     app.logger.exception(e)
    #     return res_json(code='system_error'), 500

    # Router
    app.register_blueprint(urls, url_prefix='/api')

    ch_pool_init(app)
    redis_pool_init(app)

    # APScheduler
    from app.services.scheduler import scheduler_init
    scheduler_init(app)

    return app
