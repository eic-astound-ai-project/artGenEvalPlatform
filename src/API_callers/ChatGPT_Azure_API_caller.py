import os
import openai
import json
import nltk
import tiktoken
nltk.download('punkt')

## Make Prompt object
def cofigt_chatGPT(path_config_file):
    # Load config values
    with open(path_config_file) as config_file:
        config_json = json.load(config_file)
    # The API key for your Azure OpenAI
    # resource.openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = config_json['API_KEY']

    # The base URL for your Azure OpenAI resource. e.g. "https://<your resource name>.openai.azure.com"
    if("OPENAI_API_BASE" in config_json.keys() and (not (config_json['OPENAI_API_BASE']==""))):
        # This is set to `azure`
        openai.api_type = "azure"
        openai.api_base = config_json['OPENAI_API_BASE']

    # Currently OPENAI API have the following versions available: 2022-12-01
    if ("OPENAI_API_VERSION" in config_json.keys() and (not (config_json['OPENAI_API_VERSION']==""))):
        openai.api_version = config_json['OPENAI_API_VERSION']
    return config_json



def num_tokens_from_messages(messages, model="gpt-3.5-turbo"):
  """Returns the number of tokens used by a list of messages."""
  try:
      encoding = tiktoken.encoding_for_model(model)
  except KeyError:
      encoding = tiktoken.get_encoding("cl100k_base")
  if model == "gpt-3.5-turbo":  # note: future models may deviate from this
      num_tokens = 0
      for message in messages:
          num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
          for key, value in message.items():
              num_tokens += len(encoding.encode(value))
              if key == "name":  # if there's a name, the role is omitted
                  num_tokens += -1  # role is always required and always 1 token
      num_tokens += 2  # every reply is primed with <im_start>assistant
      return num_tokens
  else:
      raise NotImplementedError(f"""num_tokens_from_messages() is not presently implemented for model {model}.
  See https://github.com/openai/openai-python/blob/main/chatml.md for information on how messages are converted to tokens.""")


def message_creator(system_role, prompt):
    messages = [
        {"role": "system", "content": system_role},
        {"role": "user", "content": prompt}
    ]
    return messages



def ChatGPT_API_call(messages, config_json, debug=False):
    # Count tokens:

    response = openai.ChatCompletion.create(
        engine= config_json["GPT_MODEL"], # with Azure this parameter has to be 'engine' instead of 'model'
        messages=messages,
        temperature= config_json['model_params']["temperature"],  # randomness > For temperature, higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
        max_tokens= config_json['model_params']["max_tokens"],
        top_p= config_json['model_params']["top_p"],
        frequency_penalty= config_json['model_params']["frequency_penalty"],
        presence_penalty= config_json['model_params']["presence_penalty"],
        )

    if (debug):
        answer = response["choices"][0]["message"]["content"].strip()
        print(answer)

        # Num tokens:
        print(" ------------ N TOKENS REAL -------------")
        print("Completion tokens > ", response['usage']["completion_tokens"])
        print("Prompt tokens > ", response['usage']["prompt_tokens"])
        print("Total tokens > ", response['usage']["total_tokens"])

    return response


