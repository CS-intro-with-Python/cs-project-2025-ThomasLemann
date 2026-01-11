import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s: %(message)s'
)

logging.getLogger('werkzeug').setLevel(logging.WARNING)
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)