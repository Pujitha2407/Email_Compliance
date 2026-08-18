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

    def retrieve(self, email, top_k=None, min_score=0.15):
        """
        Retrieve policies for an email.

        min_score filters out low-relevance policies so the LLM
        is not asked to weigh in on policies that clearly do not
        apply. Tune this threshold against known labeled emails.
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

        results = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0:
                continue
            if score < min_score:
                continue
            policy = self.policies[index]
            results.append({
                "policy": policy,
                "similarity_score": float(score)
            })
        return results