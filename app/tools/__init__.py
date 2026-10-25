from langchain_core.utils.function_calling import convert_to_openai_function

from app.tools.catalog_tools import check_inventory, get_product_details, recommend_products
from app.tools.order_tools import get_customer_orders, get_order_status, track_shipment
from app.tools.retrieval_tools import search_knowledge_base
from app.tools.return_tools import initiate_return

ALL_TOOLS = [
    get_product_details,
    check_inventory,
    recommend_products,
    get_order_status,
    track_shipment,
    get_customer_orders,
    initiate_return,
    search_knowledge_base,
]
TOOLS_BY_NAME = {t.name: t for t in ALL_TOOLS}
TOOL_SPECS = [{"type": "function", **convert_to_openai_function(t, strict=True)} for t in ALL_TOOLS]
