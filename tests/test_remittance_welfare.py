from src.indices.remittance_welfare import calculate_welfare_loss_row


def test_welfare_loss_non_negative():
    out = calculate_welfare_loss_row(100.0, 0.08, cashout_loss_pct=0.005)
    assert out["real_value_delivered_usd"] >= 0
    assert 0 <= out["real_value_delivered_pct"] <= 1
