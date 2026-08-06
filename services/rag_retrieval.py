import os
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer


class RAGRetrievalService:

    def __init__(self):

        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    def execute(self, clean_email):

        # -----------------------
        # Load Policies
        # -----------------------

        policy_names = []

        policy_texts = []

        for file in os.listdir("policies"):

            with open(
                os.path.join("policies", file),
                "r"
            ) as f:

                policy_names.append(file)

                policy_texts.append(f.read())

        # -----------------------
        # Create Policy Embeddings
        # -----------------------

        policy_embeddings = self.model.encode(
            policy_texts
        )

        # -----------------------
        # Create Email Embedding
        # -----------------------

        email_embedding = self.model.encode(

            clean_email["email"].body

        )

        # -----------------------
        # Create Vector Database
        # -----------------------

        dimension = policy_embeddings.shape[1]

        index = faiss.IndexFlatL2(dimension)

        index.add(

            np.array(policy_embeddings).astype("float32")

        )

        # -----------------------
        # Search Top K
        # -----------------------

        distances, indices = index.search(

            np.array([email_embedding]).astype("float32"),

            k=2

        )

        retrieved = []

        for i in indices[0]:

            retrieved.append({

                "name": policy_names[i],

                "content": policy_texts[i]

            })

        # -----------------------
        # Return
        # -----------------------

        return {

            "email": clean_email["email"],

            "metadata": clean_email["metadata"],

            "retrieved_policies": retrieved

        }