from langchain_core.tools import tool

from app.db import session as db
from app.services import order_service
from app.services.order_service import ReturnError


@tool(parse_docstring=True)
def initiate_return(order_item_id: int, reason: str) -> dict:
    """Start a return for one order item. Creates a return request; it does not approve or issue a refund.

    Args:
        order_item_id: The order_item_id from get_order_status, not the order id.
        reason: Short reason the customer gave for the return.
    """
    with db.get_session() as session:
        try:
            ret = order_service.initiate_return(session, order_item_id, reason)
        except ReturnError as e:
            return {"error": str(e)}
        return {"return_id": ret.id, "order_item_id": ret.order_item_id, "status": ret.status, "reason": ret.reason}
