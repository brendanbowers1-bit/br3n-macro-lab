"""
Legal finality reference scores by payment system.

Tier 4 manual/legal-source mappings — not mock. Each score cites a public legal
or regulatory framework. Scores are ordinal research proxies, not legal opinions.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FinalityReference:
    country: str
    payment_system: str
    rail_type: str
    legal_finality_score: float
    operational_finality_score: float
    funds_availability_score: float
    reversibility_risk_score: float
    reconciliation_quality_score: float
    settlement_failure_risk_score: float
    finality_lag_hours: float
    legal_reference: str


# Public legal/regulatory references (research proxies only).
FINALITY_REFERENCE_TABLE: list[FinalityReference] = [
    FinalityReference(
        "United States", "Fedwire Funds Service", "rtgs", 98, 97, 96, 8, 92, 5, 0.5,
        "Federal Reserve Regulation J; UCC Article 4A finality rules",
    ),
    FinalityReference(
        "United States", "ACH Network", "ach", 82, 78, 75, 35, 80, 12, 48,
        "NACHA Operating Rules; Regulation E reversibility window",
    ),
    FinalityReference(
        "United States", "Card networks (Visa/MC)", "card", 75, 72, 70, 45, 78, 15, 72,
        "Card network rules; Reg Z chargeback framework",
    ),
    FinalityReference(
        "Euro Area", "TARGET2", "rtgs", 99, 98, 97, 5, 94, 4, 0.25,
        "ECB TARGET2 Guideline; SEPA Instant Credit Transfer where applicable",
    ),
    FinalityReference(
        "Euro Area", "TIPS", "instant", 97, 96, 98, 10, 90, 6, 0.05,
        "ECB TIPS Regulation; instant settlement with irrevocability",
    ),
    FinalityReference(
        "United Kingdom", "CHAPS", "rtgs", 98, 97, 96, 7, 93, 5, 0.5,
        "Bank of England CHAPS rules; Payment Systems Regulator framework",
    ),
    FinalityReference(
        "India", "RTGS (IN)", "rtgs", 94, 90, 88, 12, 85, 10, 0.5,
        "RBI RTGS System regulations",
    ),
    FinalityReference(
        "India", "UPI", "instant", 88, 85, 92, 18, 82, 8, 0.1,
        "NPCI UPI framework; dispute resolution vs irrevocability",
    ),
    FinalityReference(
        "Mexico", "SPEI", "rtgs", 93, 91, 90, 14, 84, 9, 0.5,
        "Banxico SPEI operating rules",
    ),
    FinalityReference(
        "Brazil", "STR", "rtgs", 92, 90, 89, 15, 83, 10, 0.5,
        "BCB STR settlement system rules",
    ),
    FinalityReference(
        "Philippines", "PhilPaSS", "rtgs", 90, 87, 86, 18, 80, 12, 0.5,
        "BSP PhilPaSS regulations",
    ),
    FinalityReference(
        "Nigeria", "NIBSS Instant Payment", "instant", 85, 80, 88, 22, 75, 14, 0.2,
        "CBN payment system guidelines",
    ),
    FinalityReference(
        "Colombia", "CENIT", "rtgs", 91, 88, 87, 16, 81, 11, 0.5,
        "Banco de la República CENIT rules",
    ),
    FinalityReference(
        "Saudi Arabia", "SARIE", "rtgs", 94, 92, 91, 10, 86, 8, 0.5,
        "SAMA SARIE operating framework",
    ),
    FinalityReference(
        "United States", "Remittance corridor (RPW)", "remittance", 70, 68, 72, 40, 70, 18, 72,
        "Remittance operator contracts; RPW corridor cost structure",
    ),
    FinalityReference(
        "Mexico", "Remittance corridor (RPW)", "remittance", 68, 65, 70, 42, 68, 20, 48,
        "Cross-border MTO settlement; RPW fee/speed data",
    ),
    FinalityReference(
        "India", "Remittance corridor (RPW)", "remittance", 67, 64, 69, 44, 67, 22, 24,
        "Cross-border remittance rails; RPW corridor benchmarks",
    ),
    FinalityReference(
        "Philippines", "Remittance corridor (RPW)", "remittance", 66, 63, 68, 45, 66, 23, 24,
        "Cross-border remittance rails; RPW corridor benchmarks",
    ),
    FinalityReference(
        "Brazil", "Remittance corridor (RPW)", "remittance", 65, 62, 67, 46, 65, 24, 48,
        "Cross-border remittance rails; RPW corridor benchmarks",
    ),
    FinalityReference(
        "Nigeria", "Remittance corridor (RPW)", "remittance", 60, 58, 65, 50, 62, 28, 72,
        "Cross-border remittance rails; RPW corridor benchmarks",
    ),
    FinalityReference(
        "Colombia", "Remittance corridor (RPW)", "remittance", 64, 61, 66, 47, 64, 25, 48,
        "Cross-border remittance rails; RPW corridor benchmarks",
    ),
]


def finality_reference_rows() -> list[dict]:
    return [
        {
            "country": r.country,
            "payment_system": r.payment_system,
            "rail_type": r.rail_type,
            "legal_finality_score": r.legal_finality_score,
            "operational_finality_score": r.operational_finality_score,
            "funds_availability_score": r.funds_availability_score,
            "reversibility_risk_score": r.reversibility_risk_score,
            "reconciliation_quality_score": r.reconciliation_quality_score,
            "settlement_failure_risk_score": r.settlement_failure_risk_score,
            "finality_lag_hours": r.finality_lag_hours,
            "legal_reference": r.legal_reference,
        }
        for r in FINALITY_REFERENCE_TABLE
    ]
