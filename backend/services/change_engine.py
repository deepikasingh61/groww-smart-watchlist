def detect_meaningful_change(stock):

    price = stock["price"]
    previous_price = stock["previous_price"]
    change_percent = stock["change_percent"]

    normal_volatility = stock.get(
        "normal_volatility",
        1
    )

    target_price = stock.get("target_price")

    previous_direction = stock.get(
        "previous_direction",
        "neutral"
    )

    # Determine current direction
    if change_percent > 0:
        current_direction = "up"
    elif change_percent < 0:
        current_direction = "down"
    else:
        current_direction = "neutral"


    # =====================================
    # 1. TARGET HIT
    # =====================================

    if target_price is not None:

        crossed_up = (
            previous_price < target_price
            and price >= target_price
        )

        crossed_down = (
            previous_price > target_price
            and price <= target_price
        )

        if crossed_up or crossed_down:

            # Higher score if price moved further beyond target
            distance_from_target = abs(
                price - target_price
            ) / target_price * 100

            priority = 10 + min(
                round(distance_from_target, 1),
                3
            )

            return {
                "meaningful": True,
                "signal_type": "TARGET HIT",
                "reason": (
                    f"The price crossed your target of "
                    f"₹{target_price:,.0f} and is now "
                    f"at ₹{price:,.2f}."
                ),
                "priority": priority
            }


    # =====================================
    # 2. UNUSUAL MOVE
    # =====================================

    if (
        normal_volatility > 0
        and abs(change_percent) >= normal_volatility * 2
    ):

        multiple = (
            abs(change_percent)
            / normal_volatility
        )

        direction = (
            "up"
            if change_percent > 0
            else "down"
        )

        # Dynamic priority based on strength
        priority = 8 + min(
            round(multiple - 2, 1),
            4
        )

        return {
            "meaningful": True,
            "signal_type": "UNUSUAL MOVE",
            "reason": (
                f"This stock moved "
                f"{abs(change_percent):.2f}% {direction}, "
                f"which is {multiple:.1f}× its normal movement."
            ),
            "priority": priority
        }


    # =====================================
    # 3. REVERSAL
    # =====================================

    if (
        previous_direction != "neutral"
        and current_direction != "neutral"
        and previous_direction != current_direction
    ):

        # Stronger reversals get slightly higher priority
        movement_strength = abs(change_percent)

        priority = 6 + min(
            round(movement_strength, 1),
            2
        )

        return {
            "meaningful": True,
            "signal_type": "REVERSAL",
            "reason": (
                f"The stock reversed direction and is now "
                f"moving {current_direction} by "
                f"{abs(change_percent):.2f}%."
            ),
            "priority": priority
        }


    # =====================================
    # NOTHING MEANINGFUL
    # =====================================

    return {
        "meaningful": False,
        "signal_type": None,
        "reason": None,
        "priority": 0
    }