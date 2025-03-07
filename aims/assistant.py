
# import time
# import openai

# def wait_on_run(client, run, thread,sleep_interval = 0.1):
#     """
#     Wait for the run to complete before returning to the exterior function with OpenAI API

#     Args:
#         client (OpenAI.Client): The OpenAI API client.
#         run (OpenAI.Run): The run to wait for.
#         thread (str): The thread ID.
#         sleep_interval (float, optional): The sleep interval. Defaults to 0.1.

#     Returns:
#         OpenAI.Run: The run taken from OpenAI
#     """
#     while run.status == "queued" or run.status == "in_progress":
#         run = client.beta.threads.runs.retrieve(
#             thread_id=thread,
#             run_id=run.id
#         )
#         time.sleep(sleep_interval)
#     return run

# import time

# def oai_thread_message_asst(client,file,assistant = "ass_redacted",msg = None, msg_tokens = 200,temp = 0, wait=0.1,attempts = 2):
#     """
#     Using OpenAI, we will provide a summary for the abstract provided as a parameter to the function based on the sought after target audience for the user.

#     Args:
#         client (OpenAI.Client): The OpenAI API client.
#         record (dict): the records collected by the user from Entrez and CrossRef APIs
#         assistant (str, optional): The assistant to use for the OpenAI API. Defaults to "asst_redacted".
#         msg (str, optional): The message to use for the OpenAI API. Defaults to None.
        
#         msg_tokens (int, optional): The number of tokens to use for the OpenAI API. Defaults to 200.
#         temp (int, optional): The temperature to use for the OpenAI API. Defaults to 0.

#     Returns:
#         tuple: The thread id and the content suggestion
#     """
#     for attempt in range(attempts):  # Try twice
#         try:
            
#             thread_id = str(client.beta.threads.create().id)
            
#             if msg is None:
#                 msg = (
#                     "Process the attached VTT transcript" 
#                 )
            
#             # Add message to the thread
#             thread_message = client.beta.threads.messages.create(
#                 thread_id,
#                 role="user",
#                 content=msg,
                
#             )
            
            

#             # Run the thread
#             run = client.beta.threads.runs.create(
#                 thread_id=thread_id,
#                 assistant_id=assistant,
#                 max_completion_tokens=msg_tokens,
#                 temperature=temp,
                
#             )

#             # Wait for the run to complete
#             run = wait_on_run(client, run, thread_id, wait)

#             # Retrieve messages
#             messages = client.beta.threads.messages.list(thread_id=thread_id)
#             content_suggestion = messages.data[0].content[0].text.value

#             return thread_id, content_suggestion

#         except IndexError:
#             if attempt == 1:  # If it's the second attempt, raise the error
#                 raise
#             time.sleep(1)  # Wait a bit before retrying

# def summarizer():
#     pass
#     return 
