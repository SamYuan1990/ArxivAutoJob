# ArxivAutoJob
This repo just collect arxiv paper with [arxiv_mcp_project](https://github.com/blazickjp/arxiv-mcp-server) as a daily job in github archive.

## Update
> 2025-08-19:
If fact check leave to SEO, then we will never achieve the facts of fact check.
So... leave fact check to audience themself.

For any article, we just 
- decouple, Subject, Predicate and Object with Attributive, Adverbial and Complement and others.
- For fact in the article part, we try to re-create the facts from Subject, Predicate and Object
- And for this, we can ask question as if numbers or examples are validate or not?

- We re-create author's opinion from Attributive, Adverbial and Complement and others.
- And for this, we can filter out opinions as why I need your opinion? And see I am in what kind of environment?
- We also need be aware of sales/marketing articles, so ...

- To make self evaluate for audience, we should have sample in prompts.

But the question is, what's content should pass from paragraph one to paragraph two? as dynamic prompt parts? for now we just run fill in the middle approach.

Maybe
- Analysis article.
- Fact checks todo list.
- data visualization for different paragraph.

For weekly or month analysis
- Fact checks behaviors.
- 3D word cloud for data visualization.
- A suggestion to break information cocoon.
- Metadata, or user's own Glossary.

> 2025-08-04:
I found a new idea to analysis the content.
```
You are a professional linguist and you are currently working on an analysis of an article that will be used to teach your classmates in class. The topic is to show students how to identify communication methods and their harms in communication through practical analysis.

Please note that the author and source of this article are not reliable and not necessarily credible, so the author may be deliberately deceiving people, and a random article as a teaching case can be very helpful for students to browse content on the Internet on a daily basis.

Analysis steps:
As a first step, please score according to the following formula:
1.1 Core Component (CC) = Subject (S) Predicate (P) Object (O)
1.2 Modifier (MC) = Attributive (Attr) Adverb (Adv) Complement (Comp) Other Modifier (OM)
The second step is to sort out the emotional intensity of the modification component, since the general modification part is the author's opinion or comment, please organize the strength of this part (1~10) for scoring.
The third step is to list the possible communication methods in the original text one by one, such as
- Information screening and one-sided presentation, including but not limited to: biased generalization, selective reporting, and survivor bias
- Concept and issue manipulation, including but not limited to: stealing concepts, labeling, stigmatization, emotional kidnapping
- Factual manipulation, including but not limited to: fabricating facts, taking them out of context, and misleading data
- Communication and psychological manipulation, including but not limited to: repeated reinforcement, creating antagonism, and silence spirals
- Media environment manipulation, including but not limited to: topic setting, information overload, and authoritative endorsement
In the fourth step, based on the results of the first and third steps, construct search terms for readers to practice fact-checking.

Next, I will send you the article piece by piece.
```
json structure
```
{
  "core_components": {
    "subject": ["主语1", "主语2"],
    "predicate": ["谓语1", "谓语2"],
    "object": ["宾语1", "宾语2"]
  },
  "modifier_components": {
    "attributes": ["定语1", "定语2"],
    "adverbials": ["状语1", "状语2"],
    "complements": ["补语1", "补语2"],
    "other_modifiers": ["其他修饰语1", "其他修饰语2"],
    "emotional_intensity": 7
  },
  "communication_manipulation_techniques": {
    "information_filtering": [
      {
        "evaluation": "评价内容1",
        "fact_check_keywords": ["关键词1", "关键词2"]
      },
      {
        "evaluation": "评价内容2",
        "fact_check_keywords": ["关键词3", "关键词4"]
      }
    ],
    "concept_manipulation": [
      {
        "evaluation": "评价内容1",
        "fact_check_keywords": ["关键词1", "关键词2"]
      }
    ],
    "fact_manipulation": [
      {
        "evaluation": "评价内容1",
        "fact_check_keywords": ["关键词1", "关键词2"]
      },
      {
        "evaluation": "评价内容2",
        "fact_check_keywords": ["关键词3", "关键词4"]
      }
    ],
    "psychological_manipulation": [
      {
        "evaluation": "评价内容1",
        "fact_check_keywords": ["关键词1", "关键词2"]
      }
    ],
    "media_environment_manipulation": [
      {
        "evaluation": "评价内容1",
        "fact_check_keywords": ["关键词1", "关键词2"]
      },
      {
        "evaluation": "评价内容2",
        "fact_check_keywords": ["关键词3", "关键词4"]
      }
    ]
  }
}
```


> 2025-04-07:
I don't suppose I should use/realy on AI to read all of them.
But I want to use AI provides me a quick summary.
As leaving it at [comprehensive-analysis](https://github.com/blazickjp/arxiv-mcp-server/blob/main/src/arxiv_mcp_server/prompts/deep_research_analysis_prompt.py#L21C2-L21C24) part.
