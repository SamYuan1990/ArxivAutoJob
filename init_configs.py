from deepSeekmodel import DeepSeekModel
#from AnalysisResult import write_results_to_markdown

import yaml
import logging
import os

def init_configs():
    logging.basicConfig(
        format="%(levelname)s | %(name)s | %(message)s", 
        handlers=[logging.StreamHandler()]
    )

    logging.getLogger("strands").setLevel(logging.DEBUG)

    model = DeepSeekModel(
        api_key=os.environ["api_key"],
        base_url="https://api.deepseek.com",
        model_id="deepseek-chat",
    )

    with open("config.yaml", "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return model, config

# Create an agent with tools from the strands-tools example tools package
# as well as our custom letter_counter tool
#analysisAgent = AnalysisAgent(
#    config=config,
#    model=model
#)

#articles = split_markdown_by_headings("thepaper.md")
#articles_to_process = articles[:5]

#for i, article in enumerate(articles_to_process, 1):
#    messages = re.split(r'[。！？\n]\s*', article.strip())
#    messages = [s.strip() for s in messages if s.strip()]
#    # Ask the agent a question that uses the available tools
#    analysis_results = analysisAgent.process_messages(messages)
#    print("------")
#    print(analysis_results)
#    print("------")
#    filtered_sentences = filter_high_spo_sentences(analysis_results)
#    print("------")
#    print(filtered_sentences)
#    print("------")
#    summary_agent = SummaryAgent(
#        config=config,
#        model=model
#    )
#    summary_result = summary_agent.summary(filtered_sentences)
#    print(summary_result)
#    write_results_to_markdown(str(summary_result),analysis_results,"./test12345.md")
