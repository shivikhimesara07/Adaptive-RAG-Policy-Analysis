from agentic_loop import run_agentic_synthesis
from corpus import get_chunk
from eval_harness import run_eval
from router import AdaptiveRouter
from simulate_impact import (
    simulate_dollar_threshold_change,
    simulate_percentage_rate_change,
    simulate_visit_cap_change,
)
from synthetic_claims import generate_synthetic_episodes, generate_synthetic_imaging_claims


def header(text):
    print("\n" + "=" * 72)
    print(text)
    print("=" * 72)


def run_simulation_for_change(change: dict, episodes, imaging_claims):
    ctype = change.get("change_type")
    old_v, new_v = change.get("old_value"), change.get("new_value")
    if old_v is None or new_v is None:
        return None

    if ctype == "visit_cap":
        return simulate_visit_cap_change(episodes, int(old_v), int(new_v))
    if ctype == "dollar_threshold":
        return simulate_dollar_threshold_change(imaging_claims, float(old_v), float(new_v))
    if ctype == "percentage_rate":
        return simulate_percentage_rate_change(imaging_claims, float(old_v), float(new_v))
    return None


def print_change_and_impact(change, impact):
    status = change["final_status"]
    retries = change["retries_used"]
    print(f"\n  [{status}, retries used: {retries}]")
    print(f"  Field: {change['field_changed']}")
    if change.get("old_value") is not None:
        print(f"  {change['old_value']} -> {change['new_value']} (effective {change['effective_date']})")
    if impact:
        print(f"  Items analyzed:   {impact['total_items']}")
        print(f"  Items affected:   {impact['items_affected']} ({impact['pct_affected']}%)")
        print(f"  {impact['delta_label']}: ${impact['total_delta']:,.2f}")


def main():
    router = AdaptiveRouter()
    episodes = generate_synthetic_episodes(n_episodes=40)
    imaging_claims = generate_synthetic_imaging_claims(n_claims=30)

    queries = [
        "What is the maximum number of PT visits allowed per episode of care?",
        "How does the change in the PT visit maximum affect prior authorization requirements?",
        "Summarize all changes across all utilization management policies and quantify their financial impact.",
    ]

    for query in queries:
        header(f'QUERY: "{query}"')
        result = router.route(query)
        print(f"  Routed as: {result['tier']}  (hops used: {result['hops_used']})")
        print(f"  Retrieved chunks: {result['chunk_ids']}")

        if result["tier"] == "SIMPLE":
            chunk = get_chunk(result["chunk_ids"][0])
            print(f"\n  {chunk['doc']} - {chunk['section']} ({chunk['version']}):")
            print(f"  \"{chunk['text']}\"")

        elif result["tier"] == "MULTI_HOP":
            print("\n  Entry point(s) from vector search:", result["seed_ids"])
            print("  Reached via graph traversal:",
                  [c for c in result["chunk_ids"] if c not in result["seed_ids"]])

        else:  # COMPLEX
            changes = run_agentic_synthesis(result["chunk_ids"])
            print(f"\n  Agentic loop identified {len(changes)} change(s) to draft + verify:")
            for change in changes:
                impact = run_simulation_for_change(change, episodes, imaging_claims)
                print_change_and_impact(change, impact)

    header("CRITIC EVALUATION - MEASURED CATCH RATE")
    eval_results = run_eval(n_trials=200)
    print(f"  Trials: {eval_results['n_trials']}")
    print(f"  False-positive rate on clean quotes: "
          f"{eval_results['false_positive_rate']}% "
          f"({eval_results['clean_false_flagged']}/{eval_results['clean_total']})")
    print(f"  Catch rate, wrong-clause / quantifiable changes: "
          f"{eval_results['wrong_clause_quant_catch_rate']}% "
          f"({eval_results['wrong_clause_quant_caught']}/{eval_results['wrong_clause_quant_total']})")
    print(f"  Catch rate, wrong-clause / qualitative changes: "
          f"{eval_results['wrong_clause_qual_catch_rate']}% "
          f"({eval_results['wrong_clause_qual_caught']}/{eval_results['wrong_clause_qual_total']}) "
          f"<- known gap, no value to check")
    print(f"  Catch rate, paraphrased quotes: "
          f"{eval_results['word_edit_catch_rate']}% "
          f"({eval_results['word_edit_caught']}/{eval_results['word_edit_total']})")

if __name__ == "__main__":
    main()
