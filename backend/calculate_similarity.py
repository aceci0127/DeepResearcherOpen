from langchain_community.embeddings import OpenAIEmbeddings
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def calculate_similarity(prompt, chunks, k=3):
    """
    Given a prompt and a list of document chunks (Document objects or strings),
    calculates the cosine similarity between the prompt and each chunk using OpenAI embeddings,
    and returns the top k most similar chunks as a formatted string.
    """
    # Check if chunks is empty
    if not chunks:
        print("Warning: Empty chunks list provided to calculate_similarity")
        return "No document chunks available for similarity calculation."
        
    # Extract text from each chunk if it is a Document object
    chunk_texts = []
    for chunk in chunks:
        if hasattr(chunk, "page_content"):
            chunk_texts.append(chunk.page_content)
        else:
            chunk_texts.append(str(chunk))
            
    # If no valid chunks were found, return an error message
    if not chunk_texts:
        return "No valid document content found for similarity calculation."
        
    try:
        # Initialize the OpenAI embeddings model
        embedding_model = OpenAIEmbeddings(model='text-embedding-3-large')
        
        # Get embeddings for prompt and chunks
        prompt_embedding = embedding_model.embed_query(prompt)
        chunk_embeddings = embedding_model.embed_documents(chunk_texts)
        
        # Check if chunk_embeddings is empty
        if len(chunk_embeddings) == 0:
            return "No document chunks available for similarity calculation."
            
        # Calculate cosine similarity between prompt embedding and chunk embeddings
        prompt_embedding_reshaped = np.array(prompt_embedding).reshape(1, -1)
        chunk_embeddings_array = np.array(chunk_embeddings)
        similarities = cosine_similarity(prompt_embedding_reshaped, chunk_embeddings_array)[0]
        
        # Get the number of chunks to return (min of k and available chunks)
        k = min(k, len(chunk_texts))
        top_indices = similarities.argsort()[::-1][:k]
        
        result = ""
        for i, index in enumerate(top_indices):
            result += f"chunk {i+1}: {chunk_texts[index]}\n\n\n"
            
        return result
        
    except Exception as e:
        print(f"Error in similarity calculation: {str(e)}")
        return f"Error calculating similarity: {str(e)}"