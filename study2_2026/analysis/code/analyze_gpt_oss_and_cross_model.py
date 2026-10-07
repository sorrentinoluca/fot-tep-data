"""Frozen R07 exploratory descriptive analysis; run only after authorized truth opening.

Input JSONL rows: model, key, state, predicted_label, attempts,
recoverable_transport_attempts. State is one of valid, abstain, invalid,
truncated, recoverable_transport, uncertain, missing. Every planned semantic
key has exactly one row per model. A valid row has a label; other states have
null predicted_label. Attempt counts are derived from each model's original
durable ledger, not guessed from final state. The truth manifest is the sealed
S06 CASE_MANIFEST.jsonl. This module is never imported by a sender.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

import numpy as np

ARMS = ("A0", "B0", "FULL", "SELF", "AGG", "S0", "PL0")
RECEIVERS = ("C_F1", "C_F2", "C_F3", "C_F8", "C_F10", "C_F13", "C_F14", "C_F15")
FAULTS = ("F1", "F2", "F3", "F8", "F10", "F13", "F14", "F15")
TIERS = {"A0": 1, "B0": 1, "FULL": 2, "SELF": 2, "AGG": 3, "S0": 4, "PL0": 4}
TERMINAL = {"valid", "abstain", "invalid", "truncated"}
STATES = TERMINAL | {"recoverable_transport", "uncertain", "missing"}
CONTRASTS = {
    "FULL-B0": {"FULL": 1, "B0": -1},
    "B0-A0": {"B0": 1, "A0": -1},
    "SELF-A0": {"SELF": 1, "A0": -1},
    "FULL-SELF": {"FULL": 1, "SELF": -1},
    "interaction": {"FULL": 1, "SELF": -1, "B0": -1, "A0": 1},
    "AGG-FULL": {"AGG": 1, "FULL": -1},
    "S0-B0": {"S0": 1, "B0": -1},
    "PL0-B0": {"PL0": 1, "B0": -1},
    "B0-PROTO": {"B0": 1, "PROTO": -1},
}
SEED = 20261007
RESAMPLES = 20000
COLLISION_CASE = "case_208de85d389949569608a5a94d4dd19a"
TRUTH_MANIFEST_SHA = "d8b5f379815c3fb5c3ddc1a7ef4c84fcb19efc8ff15e462a1576e082622993a4"
NUMERICAL_PREDICTIONS_SHA = "55c125a1b09091a45c7a149970129d8b363c839f5121d436ba738e37d970eea3"


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(truth_path, output_path, numerical_path):
    if sha(truth_path) != TRUTH_MANIFEST_SHA or sha(numerical_path) != NUMERICAL_PREDICTIONS_SHA:
        raise ValueError("sealed truth/numerical source digest differs")
    cases = {}
    for line in Path(truth_path).open(encoding="utf-8"):
        x = json.loads(line)
        cid = x["case_id"]
        if cid in cases or x["true_label"] not in (*FAULTS, "Normal"):
            raise ValueError("duplicate case or invalid class")
        if x["owner_client_id"] != (None if x["true_label"] == "Normal" else "C_" + x["true_label"]):
            raise ValueError("owner/class mismatch")
        cases[cid] = {"label": x["true_label"], "run": x["run_id"], "owner": x["owner_client_id"]}
    if len(cases) != 256 or len({x["run"] for x in cases.values()}) != 256:
        raise ValueError("expected 256 independent physical runs")
    if Counter(x["label"] for x in cases.values()) != Counter({**{f: 24 for f in FAULTS}, "Normal": 64}):
        raise ValueError("fault allocation differs")
    outputs = defaultdict(dict)
    for line in Path(output_path).open(encoding="utf-8"):
        x = json.loads(line)
        if set(x) != {"model", "key", "state", "predicted_label", "attempts", "recoverable_transport_attempts"}:
            raise ValueError("output row schema differs")
        model, key, state = x["model"], x["key"], x["state"]
        cid, receiver, arm = key.split("|")
        if model not in ("qwen", "gptoss") or cid not in cases or receiver not in RECEIVERS or arm not in ARMS or state not in STATES:
            raise ValueError("unknown output identity/state")
        pred = x["predicted_label"]
        attempts, recoverable = x["attempts"], x["recoverable_transport_attempts"]
        if (type(attempts) is not int or type(recoverable) is not int or
                not 0 <= recoverable <= attempts <= (2 if model == "qwen" else 3) or
                (state in TERMINAL | {"recoverable_transport", "uncertain"} and attempts == 0)):
            raise ValueError("attempt count/state mismatch")
        if (state == "valid" and pred not in (*FAULTS, "Normal")) or (state != "valid" and pred is not None):
            raise ValueError("prediction/state mismatch")
        if key in outputs[model]:
            raise ValueError("duplicate output key")
        outputs[model][key] = (state, pred, attempts, recoverable)
    expected = {f"{cid}|{receiver}|{arm}" for cid in cases for receiver in RECEIVERS for arm in ARMS}
    if set(outputs) != {"qwen", "gptoss"}:
        raise ValueError("both frozen model tracks are required")
    for model, rows in outputs.items():
        if set(rows) != expected:
            raise ValueError(f"{model} key set differs from the sealed 14,336-key grid")
    numerical = {}
    for line in Path(numerical_path).open(encoding="utf-8"):
        x = json.loads(line)
        if x["case_id"] in numerical or x["case_id"] not in cases:
            raise ValueError("duplicate or unknown numerical case")
        if x["protoLabel"] not in (*FAULTS, "Normal", None) or not isinstance(x["protoAbstain"], bool):
            raise ValueError("invalid numerical prediction")
        numerical[x["case_id"]] = x["protoLabel"] if not x["protoAbstain"] else None
    if set(numerical) != set(cases):
        raise ValueError("numerical reference case set differs")
    return cases, outputs, numerical


def domain_cases(cases, fault_set, visibility):
    if visibility == "Normal":
        return [cid for cid, x in cases.items() if x["label"] == "Normal"]
    return [cid for cid, x in cases.items() if x["label"] in fault_set]


def domain_receivers(case, visibility):
    if visibility == "Normal":
        return RECEIVERS
    if visibility == "own":
        return (case["owner"],)
    return tuple(r for r in RECEIVERS if r != case["owner"])


def complete(outputs, model, cases, selected, visibility, coefficients):
    required_tiers = {TIERS[a] for a in coefficients if a != "PROTO"}
    required_arms = [a for a in ARMS if TIERS[a] in required_tiers]
    return all(outputs[model][f"{cid}|{receiver}|{arm}"][0] in TERMINAL
               for cid in selected for receiver in domain_receivers(cases[cid], visibility)
               for arm in required_arms)


def run_effects(outputs, numerical, model, cases, selected, visibility, coefficients):
    values = {}
    for cid in selected:
        label = cases[cid]["label"]
        receivers = domain_receivers(cases[cid], visibility)
        def correct(receiver, arm):
            if arm == "PROTO":
                return float(numerical[cid] == label)
            state, pred, _, _ = outputs[model][f"{cid}|{receiver}|{arm}"]
            return float(state == "valid" and pred == label)
        values[cid] = sum(weight * np.mean([correct(r, arm) for r in receivers])
                          for arm, weight in coefficients.items())
    return values


def estimate(cases, values, selected, visibility):
    if visibility == "Normal":
        return float(np.mean([values[cid] for cid in selected]))
    by_fault = defaultdict(list)
    for cid in selected:
        by_fault[cases[cid]["label"]].append(values[cid])
    return float(np.mean([np.mean(v) for v in by_fault.values()]))


def bootstrap(cases, values, selected, visibility):
    rng = np.random.Generator(np.random.PCG64(SEED))
    groups = {"Normal": selected} if visibility == "Normal" else {
        f: [cid for cid in selected if cases[cid]["label"] == f]
        for f in FAULTS if any(cases[cid]["label"] == f for cid in selected)}
    draws = []
    for group in groups.values():
        vec = np.array([values[cid] for cid in group], dtype=float)
        indices = rng.integers(0, len(vec), size=(RESAMPLES, len(vec)))
        draws.append(vec[indices].mean(axis=1))
    sample = np.mean(np.stack(draws), axis=0)
    return [float(x) for x in np.quantile(sample, [0.025, 0.975], method="linear")]


def analyze(cases, outputs, numerical):
    partitions = {"all_faults": FAULTS, "excluding_F1_F8": tuple(f for f in FAULTS if f not in ("F1", "F8")),
                  "F1_F8": ("F1", "F8")}
    domains = [(name, fs, visibility) for name, fs in partitions.items() for visibility in ("own", "local_unseen")]
    domains.extend((fault, (fault,), visibility) for fault in FAULTS for visibility in ("own", "local_unseen"))
    domains.append(("Normal", (), "Normal"))
    collision_present = COLLISION_CASE in cases
    result = {"classification": "post_Qwen_send_exploratory_descriptive", "seed": SEED,
              "resamples": RESAMPLES, "models": sorted(outputs), "contrasts": []}
    for name, fault_set, visibility in domains:
        selected = domain_cases(cases, fault_set, visibility)
        for arm in ARMS:
            coefficients = {arm: 1}
            for model in outputs:
                if complete(outputs, model, cases, selected, visibility, coefficients):
                    effects = run_effects(outputs, numerical, model, cases, selected, visibility, coefficients)
                    row = {"domain": name, "visibility": visibility,
                        "contrast": "mean_" + arm, "model": model, "plannedRuns": len(selected),
                        "estimate": estimate(cases, effects, selected, visibility)}
                    if model == "gptoss":
                        row["pointwise95"] = bootstrap(cases, effects, selected, visibility)
                    if collision_present and COLLISION_CASE in selected:
                        retained = [cid for cid in selected if cid != COLLISION_CASE]
                        row["collisionWholeRunSensitivityPointOnly"] = estimate(cases, effects, retained, visibility)
                    result["contrasts"].append(row)
        for contrast, coefficients in CONTRASTS.items():
            eligible = ("gptoss",) if contrast == "B0-PROTO" else tuple(outputs)
            available = {m: complete(outputs, m, cases, selected, visibility, coefficients) for m in eligible if m in outputs}
            values = {m: run_effects(outputs, numerical, m, cases, selected, visibility, coefficients)
                      for m, ok in available.items() if ok}
            for model, effect in values.items():
                row = {"domain": name, "visibility": visibility, "contrast": contrast, "model": model,
                       "plannedRuns": len(selected), "estimate": estimate(cases, effect, selected, visibility),
                       }
                if model == "gptoss":
                    row["pointwise95"] = bootstrap(cases, effect, selected, visibility)
                if collision_present and COLLISION_CASE in selected:
                    retained = [cid for cid in selected if cid != COLLISION_CASE]
                    row["collisionWholeRunSensitivityPointOnly"] = estimate(cases, effect, retained, visibility)
                result["contrasts"].append(row)
            if available.get("qwen") and available.get("gptoss"):
                diff = {cid: values["gptoss"][cid] - values["qwen"][cid] for cid in selected}
                row = {"domain": name, "visibility": visibility, "contrast": contrast,
                    "model": "gptoss_minus_qwen_effect", "plannedRuns": len(selected),
                    "estimate": estimate(cases, diff, selected, visibility),
                    "pointwise95": bootstrap(cases, diff, selected, visibility)}
                if collision_present and COLLISION_CASE in selected:
                    retained = [cid for cid in selected if cid != COLLISION_CASE]
                    row["collisionWholeRunSensitivityPointOnly"] = estimate(cases, diff, retained, visibility)
                result["contrasts"].append(row)
            if not all(available.values()):
                result["contrasts"].append({"domain": name, "visibility": visibility, "contrast": contrast,
                    "unavailableModels": [m for m, ok in available.items() if not ok],
                    "reason": "required tier lacks terminal HTTP 200 coverage in selected domain"})
    result["counts"] = []
    def summarize(entries):
        states = Counter(row[0] for row in entries)
        planned = len(entries)
        terminal = sum(states[state] for state in TERMINAL)
        return {"planned": planned, "attempted": sum(row[2] > 0 for row in entries),
                "transportAttempts": sum(row[2] for row in entries),
                "recoverableTransportAttempts": sum(row[3] for row in entries),
                "terminalHttp200": terminal, "valid": states["valid"], "abstain": states["abstain"],
                "invalid": states["invalid"], "truncated": states["truncated"],
                "uncertain": states["uncertain"], "recoverableTransportPending": states["recoverable_transport"],
                "missing": planned - terminal,
                "states": {state: states[state] for state in sorted(STATES)}}
    for name, fault_set, visibility in domains:
        selected = domain_cases(cases, fault_set, visibility)
        for model, rows in outputs.items():
            for arm in ARMS:
                entries = [rows[f"{cid}|{receiver}|{arm}"]
                           for cid in selected for receiver in domain_receivers(cases[cid], visibility)]
                result["counts"].append({"domain": name, "visibility": visibility, "model": model,
                                         "arm": arm, **summarize(entries)})
    if COLLISION_CASE in cases:
        result["flaggedCollisionKeys"] = [{"model": model, "arm": arm, "caseId": COLLISION_CASE,
            "receiver": "C_F2", **summarize([rows[f"{COLLISION_CASE}|C_F2|{arm}"]])}
            for model, rows in outputs.items() for arm in ARMS]
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("truth_manifest", type=Path)
    parser.add_argument("normalized_outputs", type=Path)
    parser.add_argument("numerical_predictions", type=Path)
    parser.add_argument("result", type=Path)
    args = parser.parse_args()
    if args.result.exists():
        raise FileExistsError(args.result)
    cases, outputs, numerical = load(args.truth_manifest, args.normalized_outputs, args.numerical_predictions)
    result = analyze(cases, outputs, numerical)
    result["sourceSha256"] = {"truthManifest": sha(args.truth_manifest), "normalizedOutputs": sha(args.normalized_outputs),
                              "numericalPredictions": sha(args.numerical_predictions)}
    args.result.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
