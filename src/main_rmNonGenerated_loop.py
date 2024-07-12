import argparse
import shutil
import os, sys
sys.path.append('.')
sys.path.append('..')
sys.path.append('../../')
sys.path.append('../../../')
from src.utils.args_utils import str2bool
from src.utils.response2profileJSON import clean_files, check_finish_reasons, check_complete_eval





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Configuration of the dialogue creator tool")
    parser.add_argument('-GeneratedEvalPath', '--root_path', type=str, required=True,
                        help='Path to the folder of automatically generated dialogues or automaticaly generated evaluations by LLM models')
    parser.add_argument('-removeFolders', '--remove_folders', type=str,
                        help='True if we want to clean the directory of LLM answers with incorrect formats',
                        default="False")
    parser.add_argument('-reliability_iterations', '--reliability_iterations', type=int,
                        help='If is is reliability study, indicate number of iterations, otherwise, left -1',
                        default=-1)


    args = parser.parse_args()
    response_structure = ["choices", 0, "finish_reason"]
    if(args.reliability_iterations>-1):
        total_dialogues = 0
        for iteration in range(args.reliability_iterations):
            path_root = args.root_path.replace("_repetition_0", "_repetition_"+str(iteration))
            path_error_logs = os.path.join(path_root, "ERRORS_LOGS")
            df_errors = check_complete_eval(path_root)
            # check_complete_eval
            os.makedirs(path_error_logs, exist_ok=True)
            df_errors.to_csv(os.path.join(path_error_logs, "error_logs_secondCheck.csv"), sep=";", header=True)
            print(" >>> >>> N FILES DETECTED: ", len(df_errors), " <<< <<< ")
            # Create filters:
            clean_files(df_errors, path_root, remove_folders=str2bool(args.remove_folders))
            total_dialogues+=len(df_errors)
        print("TOTAL DIALOGUES: ", str(total_dialogues))

    else:
        path_error_logs = os.path.join(args.root_path, "ERRORS_LOGS")
        if ("Generation" in args.root_path or "dialogueTests" in args.root_path or "GeneratedDialogues" in args.root_path):
            df_errors = check_finish_reasons(args.root_path, response_structure, response_name="response.json")
        elif ("Evaluation" in args.root_path):
            df_errors = check_complete_eval(args.root_path)
            # check_complete_eval

        os.makedirs(path_error_logs, exist_ok=True)
        df_errors.to_csv(os.path.join(path_error_logs, "error_logs_secondCheck.csv"), sep=";", header=True)
        print(" >>> >>> N FILES DETECTED: ", len(df_errors), " <<< <<< ")
        # Create filters:
        clean_files(df_errors, args.root_path, remove_folders=str2bool(args.remove_folders))


