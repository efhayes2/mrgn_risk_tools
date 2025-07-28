def calculate_effective_apy(
    staking_yield: float,
    lending_apy: float,
    reward_apy: float,
    borrow_apy: float,
    asset_weight_init: float,
    borrow_weight_init: float,
    max_loops: int
) -> tuple[float, float]:
    """
    Calculate the effective APY for both finite and infinite loop cases.

    Args:
        staking_yield (float): Staking yield in decimal (e.g. 0.07 for 7%)
        lending_apy (float): Lending APY in decimal
        reward_apy (float): Reward APY in decimal
        borrow_apy (float): Borrow APY in decimal
        asset_weight_init (float): Initial asset weight (e.g. 0.9)
        borrow_weight_init (float): Initial borrow weight (e.g. 1.1)
        max_loops (int): Maximum number of recursive leverage loops

    Returns:
        tuple: (effective_apy_finite, effective_apy_infinite)
    """
    if borrow_weight_init == 0:
        raise ValueError("Borrow weight cannot be zero")

    looping_factor = asset_weight_init / borrow_weight_init

    # Prevent division by zero in loop multiplier
    if looping_factor == 1:
        loop_multiples_finite = max_loops
        loop_multiples_infinite = float('inf')
    else:
        loop_multiples_finite = (1 - looping_factor ** max_loops) / (1 - looping_factor)
        loop_multiples_infinite = 1 / (1 - looping_factor) if looping_factor < 1 else float('inf')

    single_loop_yield = (
        staking_yield + lending_apy + looping_factor * (reward_apy - borrow_apy)
    )

    effective_apy_finite = loop_multiples_finite * single_loop_yield
    effective_apy_infinite = loop_multiples_infinite * single_loop_yield

    return effective_apy_finite, effective_apy_infinite


if __name__ == "__main__":
    # Example inputs
    staking_yield = 0.0725           # 7%
    lending_apy = 0.0002             # 3%
    reward_apy = 0.05              # 8%
    borrow_apy = 0.0678              # 5%
    asset_weight_init = 0.9
    borrow_weight_init = 1.25
    max_loops = 10

    finite_apy, infinite_apy = calculate_effective_apy(
        staking_yield,
        lending_apy,
        reward_apy,
        borrow_apy,
        asset_weight_init,
        borrow_weight_init,
        max_loops
    )

    print(f"Effective APY (max_loops = {max_loops}): {finite_apy:.9%}")
    print(f"Effective APY (∞ loops): {infinite_apy:.9%}" if infinite_apy != float(
        'inf') else "Effective APY (∞ loops): Infinity")