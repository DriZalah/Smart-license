"""Evaluation metrics (Eqs. 8-10).

Positive class = authorised. Events routed to manual review (S6, unresolved tourist
links, plates not accepted after re-capture) are excluded from the automatic-decision
confusion matrix of BOTH systems and reported separately.
"""
import numpy as np
import pandas as pd

from .eligibility import AUTHORIZED, UNCONFIRMED


def confusion(truth, pred):
    truth = np.asarray(truth, bool)
    pred = np.asarray(pred, bool)
    tp = int(np.sum(truth & pred))
    fn = int(np.sum(truth & ~pred))
    fp = int(np.sum(~truth & pred))
    tn = int(np.sum(~truth & ~pred))
    return tp, fn, fp, tn


def scores(tp, fn, fp, tn):
    acc = (tp + tn) / (tp + tn + fp + fn)                       # Eq. 8
    prec = tp / (tp + fp) if tp + fp else 0.0                   # Eq. 9
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return dict(accuracy=acc, precision=prec, recall=rec, f1=f1)


def wfer(w_old, w_new):
    """Eq. 10."""
    return (w_old - w_new) / w_old * 100.0 if w_old else 0.0


def evaluate(df: pd.DataFrame) -> dict:
    acc = df[df.accessible_space]
    manual = acc[acc.eligibility_proposed == UNCONFIRMED]
    auto = acc[acc.eligibility_proposed != UNCONFIRMED]
    truth = auto.authorized_truth.values
    pred_new = (auto.eligibility_proposed == AUTHORIZED).values
    pred_old = (auto.decision_old == AUTHORIZED).values
    cm_new = confusion(truth, pred_new)
    cm_old = confusion(truth, pred_old)
    tp, fn, fp, tn = cm_new
    w_old = cm_old[1]
    w_new = fn
    n_auth = int(truth.sum())
    fake = auto[auto.sticker_fake]
    res = dict(
        n_records=len(df), n_accessible=len(acc), n_manual=len(manual), n_auto=len(auto),
        n_auth_auto=n_auth, n_unauth_auto=int((~truth.astype(bool)).sum()),
        cm_new=cm_new, cm_old=cm_old,
        new=scores(*cm_new), old=scores(*cm_old),
        w_old=w_old, w_new=w_new,
        wrongful_rate_old=w_old / n_auth * 100, wrongful_rate_new=w_new / n_auth * 100,
        wfer=wfer(w_old, w_new),
        n_fake=len(fake),
        fraud_rate_new=(fake.eligibility_proposed != AUTHORIZED).mean() * 100 if len(fake) else 0.0,
        fraud_rate_old=(fake.decision_old != AUTHORIZED).mean() * 100 if len(fake) else 0.0,
        n_flagged_new=int((~pred_new).sum()),
        manual_breakdown=dict(
            s6_holder_absent=int((manual.holder_absent & manual.lpr_accepted & ~manual.tourist_link_failed).sum()),
            tourist_link_failed=int((manual.tourist_link_failed & manual.lpr_accepted).sum()),
            lpr_not_accepted=int((~manual.lpr_accepted).sum())),
        s7_multi_permit=int((acc.scenario == "S7").sum()),
        scenario_counts=acc.scenario.value_counts().sort_index().to_dict(),
    )
    t = df.verification_time_s
    res["time"] = dict(min=t.min(), p25=t.quantile(.25), median=t.median(), p75=t.quantile(.75),
                       p95=t.quantile(.95), max=t.max(), mean=t.mean())
    res["manual_time_mean"] = df.manual_time_s.mean()
    c = acc.lpr_confidence
    res["lpr"] = dict(mean=c.mean(), std=c.std(), min=c.min(), max=c.max(),
                      below=int((~acc.lpr_accepted).sum()),
                      recaptured=int((acc.lpr_captures > 1).sum()))
    tour = df[df.tourist_flag]
    td = tour[tour.tourist_disability_linked]
    res["tourist"] = dict(n=len(tour), disabled=len(td),
                          matched=int((~td.tourist_link_failed).sum()),
                          failed=int(td.tourist_link_failed.sum()))
    return res
