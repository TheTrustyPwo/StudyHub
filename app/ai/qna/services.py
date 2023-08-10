import json

import openai
import pinecone

EMBEDDINGS_MODEL = "text-embedding-ada-002"
GENERATIVE_MODEL = "gpt-3.5-turbo"
COSINE_SIM_THRESHOLD = 0.7
TOP_K = 10


def answer(question):
    search_query_embedding = openai.Engine(id=EMBEDDINGS_MODEL).embeddings(input=[question])["data"][0]["embedding"]

    try:
        query_response = pinecone.Index('studyhub').query(
            top_k=TOP_K,
            include_values=False,
            include_metadata=True,
            vector=search_query_embedding,
        )

        with open('app/ai/qna/file-text-mapping.json', 'r') as fp:
            file_text_dict = json.load(fp)

        files_string = "Extract:\n"

        for i in range(len(query_response.matches)):
            result = query_response.matches[i]
            file_chunk_id = result.id

            score = result.score
            if score < COSINE_SIM_THRESHOLD and i > 0:
                break

            topic = result.metadata["topic"]
            file_text = file_text_dict.get(file_chunk_id)
            files_string += f"\nTopic: {topic}\nContent: {file_text}\n"

        messages = [
            {
                "role": "system",
                "content": """You are an intelligent teaching assistant whose goal is to answer and explain queries from the student.

Along with the student's question, you will be given extracts from the textbook (showing both topic and contents) to help you better assist the student. First, check if the student's question is related to the subject at hand (Physics). If not, reply "This is not a valid question.".

You will then go through the extracts to find answers to the student's question. If it is not found, use your own knowledge on the topic to give a reliable and accurate answer to the student. Make references to the textbook in your answer if possible."""
            },
            {
                "role": "user",
                "content": f"Question: {question}\n{files_string}"
            }
        ]

        response = openai.ChatCompletion.create(
            messages=messages,
            model=GENERATIVE_MODEL,
            max_tokens=1000,
            temperature=0.5,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return str(e)
