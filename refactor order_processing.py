TAX_RATE = 0.21

SAVE10_RATE = 0.10
SAVE20_RATE = 0.20
SAVE20_SMALL_RATE = 0.05

VIP_DISCOUNT_BIG = 50
VIP_DISCOUNT_SMALL = 10
VIP_MIN_SUBTOTAL = 100


def parse_request(request: dict):
    return (
        request.get("user_id"),
        request.get("items"),
        request.get("coupon"),
        request.get("currency"),
    )


def validate_request(user_id, items):
    if user_id is None:
        raise ValueError("user_id is required")
    if items is None:
        raise ValueError("items is required")
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if not items:
        raise ValueError("items must not be empty")

    for item in items:
        validation(item)


def validation(item):
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    if item["price"] <= 0:
        raise ValueError("price must be positive")
    if item["qty"] <= 0:
        raise ValueError("qty must be positive")


def calculate_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items)


def calculate_discount(subtotal, coupon):
    if not coupon:
        return 0

    if coupon == "SAVE10":
        return int(subtotal * SAVE10_RATE)

    if coupon == "SAVE20":
        if subtotal >= 200:
            return int(subtotal * SAVE20_RATE)
        return int(subtotal * SAVE20_SMALL_RATE)

    if coupon == "VIP":
        return VIP_DISCOUNT_BIG if subtotal >= VIP_MIN_SUBTOTAL else VIP_DISCOUNT_SMALL

    raise ValueError("unknown coupon")


def calculate_tax(amount):
    return int(amount * TAX_RATE)


def generate_order_id(user_id, items):
    return f"{user_id}-{len(items)}-X"


def process_checkout(request: dict) -> dict:
    user_id, items, coupon, currency = parse_request(request)
    currency = currency or "USD"

    validate_request(user_id, items)

    subtotal = calculate_subtotal(items)
    discount = calculate_discount(subtotal, coupon)

    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax(total_after_discount)
    total = total_after_discount + tax

    return {
        "order_id": generate_order_id(user_id, items),
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }
