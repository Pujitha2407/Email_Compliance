from sentence_transformers import SentenceTransformer
import faiss


class RAGRetriever:

    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.policy_index = None
        self.policies = []

    def _policy_to_text(self, policy):

        violations = "\n".join(
            f"- {item}"
            for item in policy["violations"]
        )

        exceptions = "\n".join(
            f"- {item}"
            for item in policy["exceptions"]
        )

        examples = "\n".join(
            f"- {item}"
            for item in policy["examples"]
        )

        return f"""
Policy ID: {policy["policy_id"]}
Category: {policy["category"]}
Title: {policy["title"]}

Definition:
{policy["definition"]}

Violations:
{violations}

Exceptions:
{exceptions}

Examples:
{examples}
"""

    def build_index(self, policies):

        self.policies = policies

        policy_texts = [
            self._policy_to_text(policy)
            for policy in policies
        ]

        for i in range(len(policy_texts)):
            print(
                f"Policy {i + 1} Text:\n"
                f"{policy_texts[i]}\n"
            )

        embeddings = self.model.encode(
            policy_texts,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings = embeddings.astype("float32")

        dimension = embeddings.shape[1]

        self.policy_index = faiss.IndexFlatIP(
            dimension
        )

        self.policy_index.add(embeddings)

        print(
            "Built Policy Model Index with ",
            len(policies),
            " policies."
        )

    def retrieve(
        self,
        email,
        top_k=4,
        min_similarity=0.20
    ):

        email_text = f"""
From: {email["from"]}
To: {email["to"]}
Subject: {email["subject"]}

Body:
{email["body"]}
"""

        email_embedding = self.model.encode(
            [email_text],
            convert_to_numpy=True,
            normalize_embeddings=True
        ).astype("float32")

        scores, indices = self.policy_index.search(
            email_embedding,
            len(self.policies)
        )

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index < 0:
                continue

            results.append({
                "policy": self.policies[index],
                "similarity_score": float(score)
            })

        filtered_results = [
            item
            for item in results
            if item["similarity_score"] >= min_similarity
        ]

        if not filtered_results and results:
            filtered_results = results[:1]

        filtered_results.sort(
            key=lambda item: (
                -item["similarity_score"],
                item["policy"]["policy_id"]
            )
        )

        return filtered_results[:top_k]