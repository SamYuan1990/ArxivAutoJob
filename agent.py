import json

prompt = """
please help analysis the papaer from paper's title, abstract, introduction and conclusions.
I need you give me position_index_comments, position_index, initiative_index_comments, initiative_index in json format.
The define of position_index is where the paper major discussion about, it's value of training, post training, prompt, external data mgr or multiple agents.
For example
 - an arch like RNN or transformer is training.
 - RL process like DeepSeek GPRO is post training.
 - Prompt eng skill like ReAct is prompt.
 - RAG, Memory mgr, tool call or MCP is external data mgr
 - A2A protocol is multiple agents.
The define of initiative_index is hard code style, code impls, auto adjust according to specific metric, auto adjust leave to LLM.

A paper may belongs to multiple areas or values, you need to give all belongs value. Here is the content:
"""

def analysis(client,paper_data):
    specific_prompt = prompt +'\n'+paper_data['title']+'\n'+paper_data['abstract']+'\n'+paper_data['introduction']+'\n'+paper_data['conclusions']
    messages = [{"role": "user", "content": specific_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        }
    )

    result = json.loads(response.choices[0].message.content)
    print(result)
    return result