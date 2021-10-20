from quotes import *

all_quotes = get_all_quotes()

sentences = [quote["content"] for quote in all_quotes]
sentence_tuples = [(quote["content"], quote["_id"]) for quote in all_quotes]

from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('bert-base-nli-mean-tokens')
sentence_embeddings = model.encode(sentences)
sentence_embeddings.shape

from sklearn.metrics.pairwise import cosine_similarity

for i in range(len(sentences)):
    if i == 0:
        all_other_sentence_embeddings = sentence_embeddings[1:]
    elif i == len(sentence_embeddings) - 1:
        all_other_sentence_embeddings = sentence_embeddings[0:i]
    else:
        all_other_sentence_embeddings = np.append(sentence_embeddings[0:i], sentence_embeddings[i + 1:], axis = 0)
    embeddings_for_single_sentence = sentence_embeddings[i]

    cosine_similarity_result = cosine_similarity([embeddings_for_single_sentence], all_other_sentence_embeddings)
    cosine_similarity_row = np.insert(cosine_similarity_result, i, 0, axis = 1)
    if i == 0:
        cosine_similarity_matrix = cosine_similarity_row
    else:
        cosine_similarity_matrix = np.append(cosine_similarity_matrix, cosine_similarity_row, axis = 0)

quote_ids = [quote["_id"] for quote in all_quotes]
df = pd.DataFrame(cosine_similarity_matrix, columns = quote_ids)
df["index"] = quote_ids
df = df.set_index('index')

df.to_csv("sentence_similarity_matrix.csv")