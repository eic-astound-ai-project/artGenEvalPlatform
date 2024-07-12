import argparse, os
#REDUCE RANDOMNESS:
import random, time
import openai
import numpy as np



def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def seed_libs(seed=2020):
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    np.random.seed(seed)



def response_processor(path_response, response_structure):
    print("to do")




def exception_handler(e, row, prompt, logger):
    # @author: Ivan Martín Fernández (imartinf)
    # Print which row caused the error
    logger.error(row)
    # Print the prompt that caused the error
    logger.error(prompt)
    if isinstance(e, openai.error.APIError):
        # Handle API error
        logger.error("An `APIError` indicates that something went wrong on our side when processing your request. This could be due to a temporary error, a bug, or a system outage.")
        logger.error(e)
        # Wait 10 seconds and go back to the try line
        logger.error("Waiting 10 seconds and trying again...")
        time.sleep(10)
        return True, "APIError"
    elif isinstance(e, openai.error.AuthenticationError):
        # Handle authentication error
        logger.error("An `AuthenticationError` indicates that your API key is missing or invalid.")
        logger.error(e)
        return True, "AuthenticationError" # False antes
    elif isinstance(e, openai.error.InvalidRequestError):
        # Handle invalid request error
        logger.error("An `InvalidRequestError` indicates that your request is invalid, generally due to invalid parameters.")
        logger.error(e)
        return True, "InvalidRequestError" # False antes
    elif isinstance(e, openai.error.RateLimitError):
        # Handle rate limit error
        logger.error("A `RateLimitError` indicates that you've hit a rate limit.")
        logger.error(e)
        logger.error("Waiting 1 minute to reset the rate limit...")
        time.sleep(60)
        return True, "RateLimitError"
    elif isinstance(e, openai.error.Timeout):
        # Handle timeout error
        logger.error("A `Timeout` indicates that the request timed out.")
        logger.error(e)
        # Wait 10 seconds and go back to the try line
        logger.error("Waiting 10 seconds and trying again...")
        time.sleep(10)
        return True, "Timeout"
    elif isinstance(e, openai.error.ServiceUnavailableError):
        # Handle service unavailable error
        logger.error("A `ServiceUnavailableError` indicates that we're experiencing unexpected technical difficulties.")
        logger.error(e)
        # Wait 3 minutes and go back to the try line
        logger.error("Waiting 3 minutes and trying again...")
        time.sleep(180)
        return True, "ServiceUnavailableError"
    else:
        # Handle generic OpenAI error
        logger.error("An unexpected error occurred.")
        logger.error(e)
        return True, "UnexceptecError" # False antes