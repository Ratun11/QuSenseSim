from __future__ import annotations

VARIANT_CATALOG = {
    "baseline": {
        "family": "None",
        "category": "none",
        "label": "No Mitigation",
        "parameter_name": "none",
        "parameter_value": 0,
        "scope_kind": "none",
        "profile": {
            "t1_multiplier": 1.0,
            "t2_multiplier": 1.0,
            "noise_alpha_multiplier": 1.0,
            "noise_post_gain": 1.0,
            "estimate_gain": 1.0,
            "fi_gain": 1.0,
            "instability_amplitude": 0.0,
            "detail_variables": {},
        },
    },

    "dd_pulses_1": {
        "family": "DD",
        "category": "execution",
        "label": "DD (pulses=1)",
        "parameter_name": "pulses",
        "parameter_value": 1,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.03,
            "t2_multiplier": 1.12,
            "noise_alpha_multiplier": 0.96,
            "noise_post_gain": 0.97,
            "estimate_gain": 1.00,
            "fi_gain": 1.04,
            "instability_amplitude": 0.000,
            "detail_variables": {"pulses_dd": 1},
        },
    },
    "dd_pulses_2": {
        "family": "DD",
        "category": "execution",
        "label": "DD (pulses=2)",
        "parameter_name": "pulses",
        "parameter_value": 2,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.05,
            "t2_multiplier": 1.24,
            "noise_alpha_multiplier": 0.93,
            "noise_post_gain": 0.95,
            "estimate_gain": 1.01,
            "fi_gain": 1.08,
            "instability_amplitude": 0.000,
            "detail_variables": {"pulses_dd": 2},
        },
    },
    "dd_pulses_4": {
        "family": "DD",
        "category": "execution",
        "label": "DD (pulses=4)",
        "parameter_name": "pulses",
        "parameter_value": 4,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.08,
            "t2_multiplier": 1.40,
            "noise_alpha_multiplier": 0.88,
            "noise_post_gain": 0.92,
            "estimate_gain": 1.02,
            "fi_gain": 1.13,
            "instability_amplitude": 0.001,
            "detail_variables": {"pulses_dd": 4},
        },
    },

    "rc_level_1": {
        "family": "RC",
        "category": "execution",
        "label": "RC (level=1)",
        "parameter_name": "level",
        "parameter_value": 1,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.01,
            "t2_multiplier": 1.06,
            "noise_alpha_multiplier": 0.97,
            "noise_post_gain": 0.98,
            "estimate_gain": 1.00,
            "fi_gain": 1.03,
            "instability_amplitude": 0.000,
            "detail_variables": {"level_rc": 1},
        },
    },
    "rc_level_2": {
        "family": "RC",
        "category": "execution",
        "label": "RC (level=2)",
        "parameter_name": "level",
        "parameter_value": 2,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.02,
            "t2_multiplier": 1.09,
            "noise_alpha_multiplier": 0.95,
            "noise_post_gain": 0.96,
            "estimate_gain": 1.01,
            "fi_gain": 1.06,
            "instability_amplitude": 0.001,
            "detail_variables": {"level_rc": 2},
        },
    },
    "rc_level_3": {
        "family": "RC",
        "category": "execution",
        "label": "RC (level=3)",
        "parameter_name": "level",
        "parameter_value": 3,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.03,
            "t2_multiplier": 1.12,
            "noise_alpha_multiplier": 0.93,
            "noise_post_gain": 0.94,
            "estimate_gain": 1.02,
            "fi_gain": 1.08,
            "instability_amplitude": 0.001,
            "detail_variables": {"level_rc": 3},
        },
    },

    "pt_level_1": {
        "family": "PT",
        "category": "execution",
        "label": "PT (level=1)",
        "parameter_name": "level",
        "parameter_value": 1,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.02,
            "t2_multiplier": 1.04,
            "noise_alpha_multiplier": 0.98,
            "noise_post_gain": 0.97,
            "estimate_gain": 1.00,
            "fi_gain": 1.04,
            "instability_amplitude": 0.000,
            "detail_variables": {"level_pt": 1},
        },
    },
    "pt_level_2": {
        "family": "PT",
        "category": "execution",
        "label": "PT (level=2)",
        "parameter_name": "level",
        "parameter_value": 2,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.03,
            "t2_multiplier": 1.07,
            "noise_alpha_multiplier": 0.96,
            "noise_post_gain": 0.95,
            "estimate_gain": 1.01,
            "fi_gain": 1.07,
            "instability_amplitude": 0.001,
            "detail_variables": {"level_pt": 2},
        },
    },
    "pt_level_3": {
        "family": "PT",
        "category": "execution",
        "label": "PT (level=3)",
        "parameter_name": "level",
        "parameter_value": 3,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.05,
            "t2_multiplier": 1.10,
            "noise_alpha_multiplier": 0.94,
            "noise_post_gain": 0.93,
            "estimate_gain": 1.02,
            "fi_gain": 1.10,
            "instability_amplitude": 0.001,
            "detail_variables": {"level_pt": 3},
        },
    },

    "zne_lambda_2": {
        "family": "ZNE",
        "category": "post",
        "label": "ZNE (λ=2)",
        "parameter_name": "lambda",
        "parameter_value": 2,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.02,
            "noise_alpha_multiplier": 0.97,
            "noise_post_gain": 0.96,
            "estimate_gain": 1.00,
            "fi_gain": 1.08,
            "instability_amplitude": 0.002,
            "detail_variables": {"lambda_zne": 2},
        },
    },
    "zne_lambda_3": {
        "family": "ZNE",
        "category": "post",
        "label": "ZNE (λ=3)",
        "parameter_name": "lambda",
        "parameter_value": 3,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.04,
            "noise_alpha_multiplier": 0.95,
            "noise_post_gain": 0.93,
            "estimate_gain": 1.01,
            "fi_gain": 1.13,
            "instability_amplitude": 0.004,
            "detail_variables": {"lambda_zne": 3},
        },
    },
    "zne_lambda_5": {
        "family": "ZNE",
        "category": "post",
        "label": "ZNE (λ=5)",
        "parameter_name": "lambda",
        "parameter_value": 5,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.06,
            "noise_alpha_multiplier": 0.93,
            "noise_post_gain": 0.89,
            "estimate_gain": 1.02,
            "fi_gain": 1.20,
            "instability_amplitude": 0.007,
            "detail_variables": {"lambda_zne": 5},
        },
    },

    "pec_alpha_01": {
        "family": "PEC",
        "category": "post",
        "label": "PEC (α=0.1)",
        "parameter_name": "alpha",
        "parameter_value": 0.1,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.04,
            "noise_alpha_multiplier": 0.92,
            "noise_post_gain": 0.92,
            "estimate_gain": 1.01,
            "fi_gain": 1.10,
            "instability_amplitude": 0.004,
            "detail_variables": {"alpha_pec": 0.1},
        },
    },
    "pec_alpha_02": {
        "family": "PEC",
        "category": "post",
        "label": "PEC (α=0.2)",
        "parameter_name": "alpha",
        "parameter_value": 0.2,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.05,
            "noise_alpha_multiplier": 0.88,
            "noise_post_gain": 0.88,
            "estimate_gain": 1.02,
            "fi_gain": 1.16,
            "instability_amplitude": 0.010,
            "detail_variables": {"alpha_pec": 0.2},
        },
    },
    "pec_alpha_03": {
        "family": "PEC",
        "category": "post",
        "label": "PEC (α=0.3)",
        "parameter_name": "alpha",
        "parameter_value": 0.3,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.06,
            "noise_alpha_multiplier": 0.84,
            "noise_post_gain": 0.84,
            "estimate_gain": 1.03,
            "fi_gain": 1.22,
            "instability_amplitude": 0.016,
            "detail_variables": {"alpha_pec": 0.3},
        },
    },

    "cdr_refs_4": {
        "family": "CDR",
        "category": "post",
        "label": "CDR (refs=4)",
        "parameter_name": "refs",
        "parameter_value": 4,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.03,
            "noise_alpha_multiplier": 0.96,
            "noise_post_gain": 0.96,
            "estimate_gain": 1.03,
            "fi_gain": 1.07,
            "instability_amplitude": 0.001,
            "detail_variables": {"refs_cdr": 4},
        },
    },
    "cdr_refs_8": {
        "family": "CDR",
        "category": "post",
        "label": "CDR (refs=8)",
        "parameter_name": "refs",
        "parameter_value": 8,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.05,
            "noise_alpha_multiplier": 0.94,
            "noise_post_gain": 0.94,
            "estimate_gain": 1.05,
            "fi_gain": 1.10,
            "instability_amplitude": 0.001,
            "detail_variables": {"refs_cdr": 8},
        },
    },
    "cdr_refs_16": {
        "family": "CDR",
        "category": "post",
        "label": "CDR (refs=16)",
        "parameter_name": "refs",
        "parameter_value": 16,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.01,
            "t2_multiplier": 1.08,
            "noise_alpha_multiplier": 0.91,
            "noise_post_gain": 0.92,
            "estimate_gain": 1.07,
            "fi_gain": 1.14,
            "instability_amplitude": 0.002,
            "detail_variables": {"refs_cdr": 16},
        },
    },

    "mem_shots_128": {
        "family": "MEM",
        "category": "post",
        "label": "MEM (shots=128)",
        "parameter_name": "shots",
        "parameter_value": 128,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.00,
            "noise_alpha_multiplier": 0.99,
            "noise_post_gain": 0.985,
            "estimate_gain": 1.02,
            "fi_gain": 1.03,
            "instability_amplitude": 0.000,
            "detail_variables": {"shots_mem": 128},
        },
    },
    "mem_shots_256": {
        "family": "MEM",
        "category": "post",
        "label": "MEM (shots=256)",
        "parameter_name": "shots",
        "parameter_value": 256,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.01,
            "noise_alpha_multiplier": 0.98,
            "noise_post_gain": 0.975,
            "estimate_gain": 1.04,
            "fi_gain": 1.05,
            "instability_amplitude": 0.000,
            "detail_variables": {"shots_mem": 256},
        },
    },
    "mem_shots_512": {
        "family": "MEM",
        "category": "post",
        "label": "MEM (shots=512)",
        "parameter_name": "shots",
        "parameter_value": 512,
        "scope_kind": "uniform_or_personalized",
        "profile": {
            "t1_multiplier": 1.00,
            "t2_multiplier": 1.02,
            "noise_alpha_multiplier": 0.97,
            "noise_post_gain": 0.965,
            "estimate_gain": 1.06,
            "fi_gain": 1.07,
            "instability_amplitude": 0.000,
            "detail_variables": {"shots_mem": 512},
        },
    },
}

EXECUTION_FAMILY_ORDER = ["DD", "RC", "PT"]
POST_FAMILY_ORDER = ["ZNE", "PEC", "CDR", "MEM"]

def get_variant(key: str) -> dict:
    return VARIANT_CATALOG.get(key, VARIANT_CATALOG["baseline"])

def list_variants() -> list[dict]:
    return [{"key": key, **value} for key, value in VARIANT_CATALOG.items()]

def _grouped(order, category):
    grouped = []
    for family in order:
        variants = [{"key": key, **value} for key, value in VARIANT_CATALOG.items() if value["family"] == family and value["category"] == category]
        grouped.append({"family": family, "category": category, "variants": variants})
    return grouped

def list_variant_families() -> dict:
    return {
        "execution": _grouped(EXECUTION_FAMILY_ORDER, "execution"),
        "post": _grouped(POST_FAMILY_ORDER, "post"),
    }

def variants_for_family(family: str) -> list[dict]:
    return [{"key": key, **value} for key, value in VARIANT_CATALOG.items() if value["family"] == family]

def compose_profile(variant_keys: list[str]) -> dict:
    profile = {
        "t1_multiplier": 1.0,
        "t2_multiplier": 1.0,
        "noise_alpha_multiplier": 1.0,
        "noise_post_gain": 1.0,
        "estimate_gain": 1.0,
        "fi_gain": 1.0,
        "instability_amplitude": 0.0,
        "detail_variables": {},
        "family": "None",
        "category": "none",
        "label": "No Mitigation",
        "parameter_name": "none",
        "parameter_value": 0,
    }
    if not variant_keys:
        return profile
    for key in variant_keys:
        variant = get_variant(key)
        vprof = variant["profile"]
        for pkey in ("t1_multiplier", "t2_multiplier", "noise_alpha_multiplier", "noise_post_gain", "estimate_gain", "fi_gain"):
            profile[pkey] *= vprof[pkey]
        profile["instability_amplitude"] += vprof["instability_amplitude"]
        profile["detail_variables"].update(vprof["detail_variables"])
        profile["family"] = variant["family"]
        profile["category"] = variant["category"]
        profile["label"] = variant["label"]
        profile["parameter_name"] = variant["parameter_name"]
        profile["parameter_value"] = variant["parameter_value"]
    return profile
