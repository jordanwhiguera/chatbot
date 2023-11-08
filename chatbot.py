import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=key)
STATUS_COMPLETED = "completed"

file = client.files.create(
    file=open("conversation.txt", "rb"),
    purpose='assistants'
)

instructions = """
You are a Wells Fargo Code of Conduct Representative who responds to the people effectively with a precise response regarding the the code of conduct at wells fargo. Follow the instructions listed below:
1. You look into the conversation.txt file attached and come up with an appropriate response that suits the best for the person's question.
2. If you don't find a match within the file then refrain from answering the question and just respond 'I'm sorry, I don't have an answer for you'
3. Do not engage in any other conversation that isn't about code of conduct at wells fargp, in case the user is asking questions outside this topic then excuse yourself from the conversation by responding 'I apologize but I only answer wells fargo code of conduct related questions.'
"""

assistant = client.beta.assistants.create(
    name="The Pharmacist",
    description="A chatbot that responds to people effectively with a precise response regarding the code of conduct at wells fargo.",
    model="gpt-4-1106-preview",
    tools= [{"type": "retrieval"}],
    file_ids=[file.id]
)
thread=client.beta.threads.create()
print(f"Your thread id is {thread.id}")

run = client.beta.threads.runs.create(
    thread_id=thread.id,
    assistant_id=assistant.id,
    instructions=instructions
    )

print(f"Your run id is {run.id}\n")

while True:
    text = input("What's your question?\n")

    message = client.beta.threads.messages.create(
        thread_id=thread.id, 
        role="user",
        content=text,
    )

    new_run = client.beta.threads.runs.create(
        thread_id=thread.id, 
        assistant_id=assistant.id, 
        instructions=instructions,
    )

    print(f"Your new run id is - {new_run.id}")

    status = None
    while status != STATUS_COMPLETED:
        run_list = client.beta.threads.runs.retrieve(
            thread_id=thread.id, 
            run_id=new_run.id
        )
        print(f"{run_list.status}\r", end="")
        status = run_list.status

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
    print(f"{'assistant' if messages.data[0].role == 'assistant' else 'user'}: {messages.data[0].content[0].text.value}")