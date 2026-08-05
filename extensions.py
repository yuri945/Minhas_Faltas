from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate


csrf = CSRFProtect()
migrate = Migrate()