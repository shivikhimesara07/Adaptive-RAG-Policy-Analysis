"""
Generates a small synthetic outpatient physical therapy claims dataset.

This is entirely fabricated data (no PHI, no real patients) - built only
to demonstrate the simulation mechanic for the hackathon POC.

Each "episode of care" is one patient's course of PT treatment for a single
injury, made up of some number of individual visit claims.
"""

import random

RATE_PER_VISIT = 85.00  # flat reimbursement rate per PT visit, for simplicity


def generate_synthetic_episodes(n_episodes: int = 40, seed: int = 7):
    """
    Returns a list of episodes, each a dict:
      {
        "episode_id": str,
        "patient_id": str,
        "diagnosis": str,
        "visits_used": int,   # how many PT visits this episode actually used
        "rate_per_visit": float,
      }

    visits_used is drawn from a distribution skewed toward the middle of a
    typical PT plan of care, with a long tail of higher-utilization episodes
    (the group a stricter visit cap would actually affect).
    """
    random.seed(seed)
    diagnoses = [
        "lumbar strain",
        "post-op knee (ACL repair)",
        "rotator cuff tendinopathy",
        "cervical radiculopathy",
        "ankle sprain, grade II",
        "post-op hip replacement",
    ]

    episodes = []
    for i in range(n_episodes):
        # most episodes cluster 6-14 visits, some run long (15-24)
        if random.random() < 0.35:
            visits = random.randint(13, 24)
        else:
            visits = random.randint(4, 12)

        episodes.append(
            {
                "episode_id": f"EP-{1000 + i}",
                "patient_id": f"PT-{2000 + i}",
                "diagnosis": random.choice(diagnoses),
                "visits_used": visits,
                "rate_per_visit": RATE_PER_VISIT,
            }
        )
    return episodes


def generate_synthetic_imaging_claims(n_claims: int = 30, seed: int = 11):
    """
    Returns a list of synthetic outpatient diagnostic imaging claims:
      {
        "claim_id": str,
        "patient_id": str,
        "procedure": str,
        "network_status": "in_network" | "out_of_network",
        "contracted_cost": float,  # cost band deliberately spans the
                                     # $800-$1,500 prior-auth threshold
      }
    """
    random.seed(seed)
    procedures = ["MRI - lumbar spine", "CT - abdomen/pelvis", "MRI - knee",
                  "CT - chest", "PET scan", "Ultrasound - abdomen"]

    claims = []
    for i in range(n_claims):
        cost = round(random.uniform(400, 2200), 2)
        network = "out_of_network" if random.random() < 0.3 else "in_network"
        claims.append(
            {
                "claim_id": f"IMG-{3000 + i}",
                "patient_id": f"PT-{4000 + i}",
                "procedure": random.choice(procedures),
                "network_status": network,
                "contracted_cost": cost,
            }
        )
    return claims


if __name__ == "__main__":
    for ep in generate_synthetic_episodes(10):
        print(ep)
