from src.views.admin_views import admin_bp
from src.views.home_views import home_bp
from src.views.pedido_views import pedido_bp
from src.views.produto_views import produto_bp
from src.views.relatorio_views import relatorio_bp
from src.views.usuario_views import usuario_bp

BLUEPRINTS = (home_bp, produto_bp, usuario_bp, pedido_bp, relatorio_bp, admin_bp)
