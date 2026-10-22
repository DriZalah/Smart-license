"""Entity-relationship diagram of the SLPVS database (Figure 4). Requires Graphviz `dot`."""
import os
import subprocess
import _path  # noqa: F401

ENTITIES = {
    "PERSON": ["person_id (PK)", "national_id / iqama / passport", "person_type", "contact_ref"],
    "VEHICLE": ["plate_no (PK)", "owner_person_id (FK)", "vehicle_type", "model_year"],
    "RENTAL_CONTRACT": ["contract_id (PK)", "plate_no (FK)", "renter_person_id (FK)", "start_time, end_time"],
    "DISABILITY_PERMIT": ["permit_id (PK)", "beneficiary_person_id (FK)", "guardian_person_id (FK)",
                          "source (APD / visa)", "valid_from, valid_to, status"],
    "PARKING_ZONE": ["zone_id (PK)", "city, region", "bay_coordinates", "accessible_bays"],
    "PARKING_EVENT": ["event_id (PK)", "plate_no (FK)", "zone_id (FK)", "timestamp",
                      "lpr_confidence", "eligibility_state", "scenario"],
    "ENFORCEMENT_ACTION": ["action_id (PK)", "event_id (FK)", "warden_id", "action_type",
                           "fine_amount", "appeal_status"],
    "AUDIT_LOG": ["log_id (PK)", "event_id (FK, nullable)", "actor_role", "operation",
                  "prev_hash, entry_hash"],
}
RELS = [
    ("PERSON", "VEHICLE", "owns", "1", "0..N"),
    ("PERSON", "RENTAL_CONTRACT", "rents", "1", "0..N"),
    ("VEHICLE", "RENTAL_CONTRACT", "rented under", "1", "0..N"),
    ("PERSON", "DISABILITY_PERMIT", "beneficiary / guardian", "1", "0..N"),
    ("VEHICLE", "PARKING_EVENT", "observed in", "1", "0..N"),
    ("PARKING_ZONE", "PARKING_EVENT", "located in", "1", "0..N"),
    ("PARKING_EVENT", "DISABILITY_PERMIT", "matched permit", "0..N", "0..N"),
    ("PARKING_EVENT", "ENFORCEMENT_ACTION", "results in", "1", "0..1"),
    ("PARKING_EVENT", "AUDIT_LOG", "logged in", "1", "1..N"),
]


def dot_source(font="Times"):
    lines = ['graph ER {', 'graph [rankdir=LR, splines=ortho, nodesep=0.35, ranksep=0.45, bgcolor="white", pad=0.2];',
             f'node [fontname="{font}", fontsize=11];',
             'edge [color="#404040", penwidth=1.1];']
    colours = {"PERSON": "#DCE9F7", "VEHICLE": "#DCE9F7", "RENTAL_CONTRACT": "#DCE9F7",
               "DISABILITY_PERMIT": "#E2F0D9", "PARKING_ZONE": "#FFF2CC", "PARKING_EVENT": "#FFF2CC",
               "ENFORCEMENT_ACTION": "#FCE4D6", "AUDIT_LOG": "#EDEDED"}
    for name, attrs in ENTITIES.items():
        rows = "".join(f'<TR><TD ALIGN="LEFT">{a}</TD></TR>' for a in attrs)
        lines.append(f'{name} [shape=plaintext, label=<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0" CELLPADDING="3" BGCOLOR="{colours[name]}">'
                     f'<TR><TD><B>{name}</B></TD></TR>{rows}</TABLE>>];')
    for i, (a, b, lab, ca, cb) in enumerate(RELS):
        r = f"R{i}"
        lines.append(f'{r} [shape=diamond, style=filled, fillcolor="#F4F4F4", color="#F4F4F4", fontsize=9, '
                     f'margin="0.02,0.02", label="{lab}\\n{ca} : {cb}"];')
        lines.append(f"{a} -- {r} -- {b};")
    lines.append("}")
    return "\n".join(lines)


if __name__ == "__main__":
    out = os.path.join(_path.ROOT, "results", "figures")
    os.makedirs(out, exist_ok=True)
    src = os.path.join(out, "fig4_er_diagram.dot")
    with open(src, "w") as f:
        f.write(dot_source())
    subprocess.run(["dot", "-Tpng", "-Gdpi=600", src, "-o", os.path.join(out, "fig4_er_diagram.png")], check=True)
    print("ER diagram written to", out)
