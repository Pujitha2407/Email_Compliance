from sentence_transformers import SentenceTransformer
import faiss


class RAGRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.policy_index = None
        self.policies = []

    def _policy_to_text(self, policy):
        """
        Convert policy information into searchable text.
        Examples are intentionally excluded from retrieval
        so that they do not dominate similarity matching.
        """
        violations = "\n".join(
            f"- {item}"
            for item in policy.get("violations", [])
        )
        exceptions = "\n".join(
            f"- {item}"
            for item in policy.get("exceptions", [])
        )
        return f"""
Policy ID:
{policy.get("policy_id", "")}
Category:
{policy.get("category", "")}
Title:
{policy.get("title", "")}
Definition:
{policy.get("definition", "")}
Violations:
{violations}
Exceptions:
{exceptions}
"""

    def build_index(self, policies):
        """
        Create embeddings for policies and build FAISS index.
        """
        self.policies = policies
        policy_texts = [
            self._policy_to_text(policy)
            for policy in policies
        ]

        embeddings = self.model.encode(
            policy_texts,
            convert_to_numpy=True
        )
        embeddings = embeddings.astype("float32")

        # Normalize embeddings so inner product behaves
        # like cosine similarity.
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]
        self.policy_index = faiss.IndexFlatIP(dimension)
        self.policy_index.add(embeddings)

        print(
            "Built Policy Model Index with ",
            len(policies),
            " policies."
        )

    def retrieve(self, email, top_k=None, min_score=0.05, min_results=3):
        """
        Retrieve policies for an email.

        min_score filters out very low-relevance policies so the
        LLM is not asked to weigh in on policies that clearly do
        not apply.

        min_results guarantees at least this many policies are
        always returned (the top-scoring ones), even if none of
        them clear min_score. This prevents an empty retrieval
        result, which would leave the LLM with nothing to compare
        the email against and force a false "no violation" verdict
        by default.
        """
        email_text = f"""
From:
{email["from"]}
To:
{email["to"]}
Subject:
{email["subject"]}
Body:
{email["body"]}
"""
        email_embedding = self.model.encode(
            [email_text],
            convert_to_numpy=True
        ).astype("float32")
        faiss.normalize_L2(email_embedding)

        if top_k is None:
            top_k = len(self.policies)
        top_k = min(top_k, len(self.policies))

        scores, indices = self.policy_index.search(
            email_embedding,
            top_k
        )

        all_results = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            policy = self.policies[index]
            all_results.append({
                "policy": policy,
                "similarity_score": float(score)
            })

        # Keep everything above threshold.
        filtered = [
            r for r in all_results
            if r["similarity_score"] >= min_score
        ]

        # Safety floor: never return fewer than min_results,
        # even if that means including below-threshold policies.
        # all_results is already sorted by score (FAISS returns
        # results in descending similarity order), so this keeps
        # the top N regardless of threshold.
        if len(filtered) < min_results:
            filtered = all_results[:min_results]

        return filtered