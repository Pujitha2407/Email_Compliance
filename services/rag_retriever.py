from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

class RAGRetriever:
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self.policy_index = None
        self.policies = []

    def _policy_to_text(self, policy):
        """
        Convert structured policy dictionary into searchable text.
        """
        return f"""
        Policy ID: {policy["policy_id"]}
        Category: {policy["category"]}
        Title: {policy["title"]}
        Definition:
        {policy["definition"]}
        Violations:
        {policy["violations"]}
        Exceptions:
        {policy["exceptions"]}
        Examples:
        {policy["examples"]}
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
        for i in range(len(policy_texts)):
             print(f"Policy {i+1} Text:\n{policy_texts[i]}\n")  # Debugging line

        embeddings = self.model.encode(
            policy_texts,
            convert_to_numpy=True
        )
        embeddings = embeddings.astype("float32")
        #Normalize embeddings so inner product behaves
        #like cosine similarity.
        faiss.normalize_L2(embeddings)
        dimension = embeddings.shape[1]
        self.policy_index = faiss.IndexFlatIP(dimension)
        self.policy_index.add(embeddings)
        print("Built Policy Model Index with ", len(policies), " policies.")

    def retrieve(self, email, top_k=6):
        """
        Retrieve the most relevant policies for an email.
        """
        email_text = f"""
        From: {email["from"]}
        To: {email["to"]}
        Subject: {email["subject"]}
        Body:
        {email["body"]}
        """
        email_embedding = self.model.encode(
            [email_text],
            convert_to_numpy=True
        ).astype("float32")
        faiss.normalize_L2(email_embedding)
        scores, indices = self.policy_index.search(
            email_embedding,
            top_k
        )

        results = []
        for score, index in zip(scores[0], indices[0]):
            policy = self.policies[index]
            results.append({
                "policy": policy,
                "similarity_score": float(score)
            })
        return results
"""
Critical Migration Information.

1. Your scheduled Outlook Migration Date is THE EVENING OF: May 15th
2. You need to press the "Save My Data" button (ONLY ONCE) to send us your pre-migration information.
3. You must be connected to the network before you press the button.
4. If a POP-UP BOX appears, prompting you to "ABORT, CANCEL OR TRUST SIGNER" please select TRUST SIGNER.
5. Any information you Add to your Personal Address Book, Journal or calendar after you click on the button will need to be manually re-added into Outlook after you have been migrated.
6. Clicking this button does not complete your migration to Outlook. Your migration will be completed the evening of your migration date.

If you have failed to click on the button means your migration activity will be canceled and WILL NOT get your Calendar, Contacts, Journal and ToDo information imported into Outlook the day of your migration and could result in up to a 2 week delay to restore this information.

If you encounter any errors please contact the resolution center @713-853-1411
"""