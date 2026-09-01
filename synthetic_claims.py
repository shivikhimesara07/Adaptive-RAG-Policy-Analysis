import random

RATE_PER_VISIT = 85.00  

def generate_synthetic_episodes(n_episodes: int = 40, seed: int = 7):
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
