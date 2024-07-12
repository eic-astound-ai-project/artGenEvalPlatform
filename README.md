# ArtGenEvalPlatform

This repository contains the code of the ArtGenEval Platform. For a detailed information about the experiments performed and the description, visit the following links:

  * [PLATFORM DESCRIPTIO] https://doi.org/10.1016/j.eswa.2024.124524
  * [DATA DESCRIPTION]



## INSTALLATION INSTRUCTIONS

install all the libraries of requirements.txt file 

    pip install -r requirements.txt

Additionally, from Python console it is necessary to follow these instructions:

    import nltk
    nltk.download('stopwords')
    nltk.download('vader_lexicon')

## GENERATION DIALOGUES

### STEP 0: Create CSV from which complete certain fields automatically of the dialogueLOOP.json/dialogue.json

Create functions to define the requirements of each version to generate a final CSV with the following structure (or similar)

    index,PP_artwork_code,PP_author_code,PP_all_emotions,PP_mode_emotions,PP_second_emotions,PP_artStyle_code,DIALOGUE_ID,HP_emotion_code,CP_anthropic_code,CP_goal_code,HP_toxicity_code,HP_bias_code,HP_role_code,HP_artStyle_code,DG_turns
    0,by-the-eure-river-1911,gustave-loiseau,{'contentment': 6},['contentment'],[],Post_Impressionism,PP--ARTWORK_000000_PP--AUTH_000000_PP--ARTSTYLE_000000_HP--EMOT_000005_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000000_HP--ROL_000000_,contentment,No,Task Oriented,No toxic comments,No biased,Student that sometimes provides correct answers while others not,24,15
    1,by-the-eure-river-1911,gustave-loiseau,{'contentment': 6},['contentment'],[],Post_Impressionism,PP--ARTWORK_000000_PP--AUTH_000000_PP--ARTSTYLE_000000_HP--EMOT_000005_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000000_HP--ROL_000000_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000001_HP--ROL_000000_,contentment,No,Task Oriented,No toxic comments,feminism,Student that sometimes provides correct answers while others not,19,15
    2,by-the-eure-river-1911,gustave-loiseau,{'contentment': 6},['contentment'],[],Post_Impressionism,PP--ARTWORK_000000_PP--AUTH_000000_PP--ARTSTYLE_000000_HP--EMOT_000005_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000000_HP--ROL_000000_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000001_HP--ROL_000000_CP--ANTHR_000000_CP--GOAL_000000_HP--TOX_000000_HP--BIAS_000002_HP--ROL_000000_,contentment,No,Task Oriented,No toxic comments,machismo,Student that sometimes provides correct answers while others not,21,18
    ...

An example for version 1 appears in: 

    ../ASTOUND_DS_V0/src/preprocessing/versionRequirementsCSVGenerators/v1Requirements.py


### STEP 1. Generate dialogues automatically - GPT 3.5


    python3 ASTOUND_DS_V0/src/main_DialoguesGenerator_loop
    --dialogueJSON
    ASTOUND_DS_V0/0publicData/input_files/1Generators/dialogue_Expert.json
    --dialogueCompletedJSON
    completedDialogue.json
    --out_dir
    ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1
    --dialogueParameters
    ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
    -update_turns_inProfile
    True
    --path2checkDialogues ""


### STEP 2. GPT 3.5 - Check incorrect evaluations generated
Check that the dialogues were correctly generated without content_filter and so on. 

To only check the dialogues that were incorrectly generated (maybe for inspecting manually why they are incorrect), run: 

    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1
    --remove_folders False


In case you want to discard them (a copy of them is saved into a folder called ERROR_logs), we will activate the flag 'remove_folders'. Hence, the new call will be:


    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1
    --remove_folders True

If some dialogues were detected as not completed, **REPEAT STEP 1 AND 2** until they are correctly generated (or you decide to discard those dialogues with 'problems')



################## EVALUATION #######################
---------------------------------------


## EVALUATION QUALITY OF PROFILES - RECOVERING CAPACITY


### STEP 1. Generation of Quality Evaluation:

Before running the code, check paths in file: ASTOUND_DS_V0/0publicData/input_files/2Evaluators/0QualityEval/dialogueQuality_Expert.json

    python3 ASTOUND_DS_V0/src/main_DialoguesGenerator_loop
    --dialogueJSON
    ASTOUND_DS_V0/0publicData/input_files/2Evaluators/0QualityEval/dialogueQuality_Expert.json
    --dialogueCompletedJSON
    autoCompletedProfile.json
    --out_dir
    ASTOUND_DS_V0/0publicData/output_files/Metrics/ProfileReconstructionQuality/ChatGPTGeneration/Generation
    --dialogueParameters
    ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
    -update_turns_inProfile False
    --path2checkDialogues
    ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1


In case some evaluation were not generated correctly, remove them by running the command below:


    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Metrics/ProfileReconstructionQuality/ChatGPTGeneration/Generation
    --remove_folders True

Repeat step 1 (STEP 1. Generation of Quality Evaluation)


### Evaluation:


Before running the command, check paths in file: ASTOUND_DS_V0/0publicData/input_files/2Evaluators/0QualityEval/metricsQuality_Expert.json

    python3 ASTOUND_DS_V0/src/main_Evaluation_Generator_loop.py 
      -CSVwithDialogueParameters
      ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
      --out_dir
      ASTOUND_DS_V0/0publicData/output_files/Metrics
      --out_EvalFolderName
      Evaluation
      --characteristic_type
      ProfileReconstructionQuality
      --metric_type
      EvaluationObjectiveMetrics
      --dialogueCompletedJSON
      autoCompletedMetric.json
      --path2checkDialogues
      ASTOUND_DS_V0/0publicData/output_files/Metrics/ProfileReconstructionQuality/ChatGPTGeneration/Generation




## EVALUATION ANTHROPIC CHARACTERISTIC


### STEP 1. GPT 3.5 - Yes/No Statements Evaluation 


    python3 ASTOUND_DS_V0/src/main_DialoguesGenerator_loop
        --dialogueJSON
        ASTOUND_DS_V0/0publicData/input_files/2Evaluators/AnthropicEval/YesNoProfileGeneratorAnthropic_gpt35.json
        --dialogueCompletedJSON
        autoCompletedProfile.json
        --out_dir
        ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35
        --dialogueParameters
        ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
        -update_turns_inProfile
        False
        -isYesNoResponse
        True
        --path2checkDialogues
        ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1

### STEP 2. GPT 3.5 - Check incorrect evaluations generated
Check that the dialogues were correctly evaluated according to the specific format (remember that LLM models are sometimes random. This is the reason why sometimes their answers do not match the required format specified, 
hence, we need to discard these answers and ask for new ones following the required format) 

To only check the dialogues that were incorrectly generated (maybe for inspecting manually why they are incorrect), run: 

    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35
    --remove_folders False


In case you want to discard them (a copy of them is saved into a folder called ERROR_logs), we will activate the flag 'remove_folders'. Hence, the new call will be:


    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35
    --remove_folders True

If some dialogues were detected as not completed, **REPEAT STEP 1 AND 2** until they are correctly generated (or you decide to discard those dialogues with 'problems' or the ChatGPT3.5 evaluation)



### STEP 3. GPT 3.5 - Compare Yes/No statements with the profile

For the anthropic characteristic, there are 2 templates that are used, depending on whether we want to extract the LLM automatic Yes/No generated metrics or the objective metrics, and are:
     
    "Anthropic": {"EvaluationYesNo" : "../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json",
     "EvaluationObjectiveMetrics" : "../0publicData/input_files/2Evaluators/AnthropicEval/SingleMetricsAnthropic_Expert.json"},


To select, complete and understand the template to be passed, check first: [EXPLANATION TEMPLATES EMPLOYED IN EVALUATION](#explanation-templates-employed-in-evaluation)
Initially the fields will be completed to follow the default tree structure presented in this repository under [Files Structure](#files-structure). 


To verify that the dialogues match with the specific Anthropic characteristic, we run the following script to compare both:


Check template: "../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json";
specially fields:

* "in_folder_ChatGPT_generated_dialogues": "../0publicData/output_files/Generated_Dialogues_v1/dialogue_ID/response.json",
* "in_folder_ChatGPT_generated_YesNoMetrics": "../0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35/dialogue_ID/responseAsProfile.json",


and next run:

    python3 ASTOUND_DS_V0/src/main_Evaluation_Generator_loop.py 
        -CSVwithDialogueParameters ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
        --out_dir ASTOUND_DS_V0/0publicData/output_files/Metrics
        --out_EvalFolderName EvaluationGPT35
        --characteristic_type Anthropic
        --metric_type EvaluationYesNo
        --dialogueCompletedJSON autoCompletedMetric.json
        --path2checkDialogues ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35

RESULTS WILL APPEAR IN: <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/EvaluationGPT35

-------------------------------------------------------

### STEP 1. GPT 4 - Yes/No Statements Evaluation 
    python3 main_DialoguesGenerator_loop
        --dialogueJSON
        ASTOUND_DS_V0/0publicData/input_files/2Evaluators/AnthropicEval/YesNoProfileGeneratorAnthropic_gpt4.json
        --dialogueCompletedJSON
        autoCompletedProfile.json
        --out_dir
        ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT4
        --dialogueParameters
        ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
        -update_turns_inProfile
        False
        -isYesNoResponse
        True
        --path2checkDialogues
        ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1

### STEP 2. GPT 4 - Check incorrect evaluations generated
We repeat what was commented in STEP2 with the evaluations of GPT4 (below we add the version in which the evaluations are discarded > remove_folders True)

    python3 ASTOUND_DS_V0/src/utils/response2profileJSON.py
    --root_path ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT4
    --remove_folders True


### STEP 3. GPT 4 - Compare Yes/No statements with the profile


Check template: "../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json";
specially fields:

* "in_folder_ChatGPT_generated_dialogues": "../0publicData/output_files/Generated_Dialogues_v1/dialogue_ID/response.json",
* "in_folder_ChatGPT_generated_YesNoMetrics": "../0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT4/dialogue_ID/responseAsProfile.json",


and next run:

    python3 ASTOUND_DS_V0/src/main_Evaluation_Generator_loop.py 
        -CSVwithDialogueParameters <root_path>/ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
        --out_dir <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics
        --out_EvalFolderName EvaluationGPT4
        --characteristic_type Anthropic
        --metric_type EvaluationYesNo
        --dialogueCompletedJSON autoCompletedMetric.json
        --path2checkDialogues ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT4

RESULTS WILL APPEAR IN: <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/EvaluationGPT4

-------------------------------------------------

### STEP 4. Evaluation with Objective Metrics

        
As in Step 3, check the correct templates before generating the evaluation. 

Check template: "../0publicData/input_files/2Evaluators/AnthropicEval/SingleMetricsAnthropic_Expert.json"; 
specially fields:
* "in_folder_ChatGPT_generated_dialogues": "../0publicData/output_files/dialogueTests/GPT35/dialogue_ID/response.json",

and next run:

     python3 ASTOUND_DS_V0/src/main_Evaluation_Generator_loop.py 
            -CSVwithDialogueParameters ASTOUND_DS_V0/0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv
            --out_dir ASTOUND_DS_V0/0publicData/output_files/Metrics_v1
            --out_EvalFolderName Evaluation
            --characteristic_type Anthropic
            --metric_type EvaluationObjectiveMetrics
            --dialogueCompletedJSON autoCompletedMetric.json
            --path2checkDialogues ASTOUND_DS_V0/0publicData/output_files/Generated_Dialogues_v1

RESULTS WILL APPEAR IN: <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics/Anthropic/ObjectiveMetrics/Evaluation

---------------------------------
### STEP 5. Join Metrics

Combine the metrics extracted from the different evaluations 

    python3 ASTOUND_DS_V0/src/visualization/metricsCSVgenerator.py 
    -metricsDirectory <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics_v1
    --out_csv <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics_v1/summaryMetrics.csv
    --out_EvalFolderNames_YesNoMetrics "['Evaluation']"
    --out_EvalFolderNames_ObjectiveMetrics "['Evaluation']"
    --characteristic_types "['Anthropic']"
    --path_profile ASTOUND_DS_V0/0publicData/output_files/Metrics/ProfileReconstructionQuality/ObjectiveMetrics/Evaluation





### STEP 5. Final Evaluation per Characteristic (TO DO - preliminary sample)
In this last step, the target is to generate a CVS with all the matches between the 3 types of Evaluations presented for the Anthropic characteristics. 
This CSV will contain a final column called: 'Final_Anthropic_Evaluation' with a True (1) or a False (0) if it matches with the orginal profile. 

    python3 ASTOUND_DS_V0/src/main_FinalEvalStrategy_loop.py 
    -in_metrics_csv <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics/summaryMetrics.csv
    --out_csv <root_path>/ASTOUND_DS_V0/0publicData/output_files/Metrics/FinalDecisionsAnthropicMetrics.csv
    --grount_truth_column EX_anthropic_code_ORIGINAL
    --LLM_columns "['EX_anthropic_code_GENERATED_EvaluationGPT35','EX_anthropic_code_GENERATED_EvaluationGPT4']"
    --objectiveMetrics_thresholds "{'subjectivity_Expert_avg':0.6}"
    --metrics_order "{0:'EX_anthropic_code_GENERATED_EvaluationGPT35', 1:'EX_anthropic_code_GENERATED_EvaluationGPT4', 2:'subjectivity_Expert_avg'}"
    --min_matches_metricsAndProfile 1
    --final_decision_column EX_finalDecisionAnthropic
    



################## VISUALIZATION #######################
---------------------------------------
1. Simple histograms - Change variables under  ### PARAMETERS ###  before plotting and then, run the command below:
  

    python3 ASTOUND_DS_V0/src/visualization/simple_plots.py 


2. Visualization in Google Collab (for Anthropic characteristic):
https://colab.research.google.com/drive/1v__h-FQ6Vc-P9IZabrPhfP2xbycXGRPO#scrollTo=2jSLgL0EvxdF



## OTHER INFO

### Citations

If you use the platform or the data derived from it, please cite the following articles:

    @article{LUNAJIMENEZ2024124524,
    title = {Evaluating emotional and subjective responses in synthetic art-related dialogues: A multi-stage framework with large language models},
    journal = {Expert Systems with Applications},
    volume = {255},
    pages = {124524},
    year = {2024},
    issn = {0957-4174},
    doi = {https://doi.org/10.1016/j.eswa.2024.124524},
    url = {https://www.sciencedirect.com/science/article/pii/S0957417424013915},
    author = {Cristina Luna-Jiménez and Manuel Gil-Martín and Luis Fernando D’Haro and Fernando Fernández-Martínez and Rubén San-Segundo}}



### License


The resources derived from the project (software and data) are released under CC BY-NC-SA 4.0 (https://creativecommons.org/licenses/by-nc-sa/4.0/deed.en)
Universidad Politécnica de Madrid (UPM) is listed as the holder of the exploitation rights of this GitHub repository software. If you are interested on using the software or the data, contact: XX 


### Files Structure
    
    
    0publicData
    ├── input_files
    │   ├── 0parameter_files
    │   │   ├──  text_processor_params.json > JSON with the text filters (lowercase & dict with substitutions)
    │   │   ├──  responseStructure.json 
    │   │   ├──  filename_codes_vXX.csv
    │   │   ├──  artemis_sample.csv
    │   │   ├── versions
    │   │   │   ├── csvWithDialoguesCodesProfilesv1.csv > CSV with the codes to generate customized dialogues
    │   ├── 1Generators
    │   │   ├── dialogue.json > JSON with the profile of the dialogues to generate and auto-complete
    │   ├── 2Evaluators
    │   │   ├── 0QualityEval
    │   │   │   ├── dialogueQuality_Expert.json
    │   │   │   ├── metricsQuality.json
    │   │   ├── AnthropicEval
    │   │   │   ├── SingleMetricsAnthropic_Expert.json
    │   │   │   ├── YesNoProfileGeneratorAnthropic.json
    │   │   │   ├── YesNoMetricAnthropic.json
    ├── output_files
    │   ├── GeneratedDialogues (also sometimes called 'dialogueTest')
    │   │   ├──DIALOGUE_ID
    │   │   │   ├── autoCompletedProfile.json/completedDialogue.json
    │   │   │   ├── modelConfig.json
    │   │   │   ├── prompt.json
    │   │   │   ├── response.json > It includes the dialogue
    │   │   │   ├── responseAsProfile.json > "Structured Dialogue as a JSON" (ideally divided by turns & actors)
    │   ├── Metrics
    │   │   ├── ProfileReconstructionQuality
    │   │   │   ├── ChatGPTGeneration
    │   │   │   │   ├──Generation
    │   │   │   │   │   ├──<dialogue_ID>
    │   │   │   │   │   │   ├──autoCompletedProfile.json
    │   │   │   │   │   │   ├──modelConfig.json
    │   │   │   │   │   │   ├──prompt.json
    │   │   │   │   │   │   ├──response.json
    │   │   │   │   │   │   ├──responseAsProfile.json
    │   │   │   ├── ObjectiveMetrics
    │   │   │   │   ├──Evaluation
    │   │   │   │   │   ├──<dialogue_ID>
    │   │   │   │   │   │   ├──autoCompletedmetric.json
    │   │   │   │   │   │   ├──completedDialogue.json
    │   │   │   │   │   │   ├──ProfileReconstructionQuality_metrics.json
    │   │   │   │   │   │   ├──responseAsProfile.json
    │   │   ├── Anthropic or Toxicity
    │   │   │   ├── ObjectiveMetrics
    │   │   │   │   ├──Evaluation
    │   │   │   │   │   ├──<dialogue_ID>
    │   │   │   │   │   │   ├──<dialogue_ID>_Dialogue.json
    │   │   │   │   │   │   ├──<dialogue_ID>_anthropic_metrics.json
    │   │   │   ├── ChatGPTYesNo
    │   │   │   │   ├──Generation
    │   │   │   │   │   ├──<dialogue_ID>
    │   │   │   │   │   │   ├──autoCompletedProfile.json
    │   │   │   │   │   │   ├──modelConfig.json
    │   │   │   │   │   │   ├──prompt.json
    │   │   │   │   │   │   ├──response.json
    │   │   │   │   │   │   ├──responseAsProfile.json
    │   │   │   │   ├──Evaluation
    │   │   │   │   │   ├──<dialogue_ID>
    │   │   │   │   │   │   ├──autoCompletedmetrics.json
    │   │   │   │   │   │   ├──<dialogue_ID>_Dialogue.json
    │   │   │   │   │   │   ├──<dialogue_ID>_anthropicYesNo_metrics.json // <dialogue_ID>_toxicityYesNo_metrics.json

"Metrics", "METRIC_NAME","ObjectiveMetrics","Evaluation"


## EXPLANATION TEMPLATES EMPLOYED IN EVALUATION
Templates (.json) to choose (and complete) in order to perform the evaluation
    
    path_templates = {
        "ProfileReconstructionQuality": {"Evaluation": "../0publicData/input_files/2Evaluators/0QualityEval/metricsQuality_Expert.json"},

        "Anthropic": {"EvaluationYesNo" : "../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json",
                      "EvaluationObjectiveMetrics" : "../0publicData/input_files/2Evaluators/AnthropicEval/SingleMetricsAnthropic_Expert.json"},

        "Toxicity": {"EvaluationYesNo" : "../0publicData/input_files/2Evaluators/ToxicityEval/YesNoMetricToxicity.json",
                      "EvaluationObjectiveMetrics" : "../0publicData/input_files/2Evaluators/ToxicityEval/SingleMetricsToxicity_Expert.json"},
    }

Fields to complete/understand in each template:

COMMON FIELDS SHARED IN SEVERAL TEMPLATES:
* "path_filename_codes": File with the correspondence between codes and specific textual definitions for each characteristic. [e.g. "../0publicData/input_files/0parameter_files/filename_codes_v1.json"]
* "params_text_processor_path": Path to the text/special characters substitution to be applied to the automatic generated answers for performing comparison between fields (generated by LLM, and those manually defined)[e.g. "../0publicData/input_files/0parameter_files/text_processor_params.json"]
* "response_parser_params": List of fields to access for rescuing the content generated by the employed LLM [e.g. "../0publicData/input_files/0parameter_files/responseStructure.json]
* "profile_auto_path_csv": CSV with all the fields included in the profile for generating the dialogues. It is employed for rescuing the values of the profile field according to the ID of the dialogue [e.g. "../0publicData/input_files/0parameter_files/versions/v1/csvWithDialoguesCodesProfilesv1.csv"]

ANTHROPIC:
* ../0publicData/input_files/2Evaluators/AnthropicEval/YesNoMetricAnthropic.json
  * "in_folder_ChatGPT_generated_dialogues": Path to the route of the dialogues. The field 'dialogue_ID' will be substitude by the specific dialogue_ID passed later as argument (Remember, that this is a general template). [e.g of value for this field "../0publicData/output_files/dialogueTests/GPT35/dialogue_ID/response.json"]
  * "in_folder_ChatGPT_generated_YesNoMetrics": [e.g. "../0publicData/output_files/Metrics/Anthropic/ChatGPTYesNo/GenerationGPT35/dialogue_ID/responseAsProfile.json"]
  * 

  


## Config.json (sample)
Locate the config.json file under src/chatbots_eval for working with the code of src/chatbots_eval/script_ChatGPT_Azure.py

    {"CHAT_GPT_MODEL":"YOUR_MODEL_NAME",
     "OPENAI_API_BASE":"xxx.openai.azure.com/",
     "OPENAI_API_VERSION": "2023-01-10-preview",
      "API_KEY":  "YOUR_API_KEY_HERE"}



