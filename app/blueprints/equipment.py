from flask import Blueprint, render_template
from app.models import Equipment, EquipmentCategory

equipment_bp = Blueprint('equipment', __name__)


@equipment_bp.route('/')
def catalog():
    items = (Equipment.query
             .filter_by(is_published=True)
             .order_by(Equipment.sort_order, Equipment.created_at)
             .all())

    categories = (EquipmentCategory.query
                  .filter_by(is_published=True)
                  .order_by(EquipmentCategory.sort_order)
                  .all())

    return render_template('equipment.html', equipment=items, categories=categories)